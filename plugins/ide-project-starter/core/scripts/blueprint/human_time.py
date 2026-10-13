# Version-Timestamp: 2026-10-13 08:14:00 AST
"""Explicit append-only timers. A timer is not proof of human attention."""
import json
from datetime import timezone
from .contracts import project_id, require, timestamp
from .ledger import digest, encode

KINDS = {'authoring', 'briefing', 'chatting', 'supervising', 'reviewing', 'rework'}


class HumanTimer:
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.project = project_id(identity)
        if ledger.read_only:
            return
        with ledger.connection() as db:
            with db:
                db.execute('CREATE TABLE IF NOT EXISTS human_transitions(seq INTEGER PRIMARY KEY,event_id TEXT UNIQUE NOT NULL,user_id TEXT NOT NULL,payload TEXT NOT NULL)')

    def transition(self, user_id, task_id, action, when, activity_kind):
        project_id(user_id); project_id(task_id); parsed = timestamp(when)
        require(action in {'start', 'pause', 'resume', 'switch', 'stop'}, 'Unsupported timer transition')
        require(activity_kind in KINDS, 'Unsupported activity kind')
        row = {'user_id': user_id, 'project_id': self.project, 'task_id': task_id,
               'action': action, 'timestamp': parsed.isoformat(), 'activity_kind': activity_kind,
               'source': 'explicit_timer'}
        identity = digest(row)
        with self.ledger.connection() as db:
            with db:
                db.execute('BEGIN IMMEDIATE')
                if db.execute('SELECT 1 FROM human_transitions WHERE event_id=?', (identity,)).fetchone():
                    return {'status': 'duplicate'}
                found = db.execute('SELECT payload FROM human_transitions WHERE user_id=? ORDER BY seq DESC LIMIT 1', (user_id,)).fetchone()
                prior = json.loads(found[0]) if found else None
                if prior:
                    require(parsed >= timestamp(prior['timestamp']), 'Timer timestamp regressed')
                active = prior is not None and prior['action'] in {'start', 'resume', 'switch'}
                same = prior is not None and prior['task_id'] == task_id and prior['project_id'] == self.project
                if action == 'start':
                    require(not active, 'Another timer is active; switch explicitly')
                elif action == 'resume':
                    require(same and prior['action'] == 'pause', 'No matching paused timer')
                elif action == 'switch':
                    require(active and not same, 'Switch needs an active different task')
                elif action == 'pause':
                    require(active and same, 'No matching active timer')
                else:
                    require(same and prior['action'] in {'start', 'resume', 'switch', 'pause'}, 'No matching timer to stop')
                from .human_history import exists, projected, amendments, effective
                interval_id=digest(['human-interval.v1',identity,self.project,user_id])
                if exists(db,'human_archive'):
                    require(not db.execute('SELECT 1 FROM human_archive WHERE interval_id=?',(interval_id,)).fetchone(),'Interval already archived; start a new timer')
                if action in {'start','resume','switch'}:
                    for interval in effective(projected(db),amendments(db)):
                        if interval['user_id']==user_id and not interval['voided'] and interval['end_at'] is not None:
                            require(not timestamp(interval['start_at'])<=parsed<timestamp(interval['end_at']),'Overlaps existing human history')
                db.execute('INSERT INTO human_transitions(event_id,user_id,payload) VALUES(?,?,?)', (identity,user_id,encode(row)))
                from .human_history import projected, amendments, effective, check_overlaps
                check_overlaps(effective(projected(db),amendments(db)))
        return {'status': 'inserted', 'basis': 'explicit_timer_not_attention_measurement'}

    def intervals(self, user_id):
        from .human_history import snapshot, effective, exists
        project_id(user_id)
        with self.ledger.connection() as db:
            db.execute('BEGIN')
            history=snapshot(db,self.project)
            rows=effective(history['intervals'],history['amendments'])
            archived={r[0] for r in db.execute('SELECT interval_id FROM human_archive')} if exists(db,'human_archive') else set()
        return [{**row,'archived':row['interval_id'] in archived} for row in rows if row['user_id']==user_id]

    def amend(self, user_id, interval_id, previous_revision, action, when, reason, replacement):
        from .human_history import initialize, projected, amendments, effective, check_overlaps
        from .contracts import opaque
        project_id(user_id); opaque(interval_id); opaque(previous_revision)
        if replacement is not None:
            require(isinstance(replacement,dict) and set(replacement)=={'task_id','activity_kind','start_at','end_at'},'Invalid correction fields')
            replacement={**replacement,'start_at':timestamp(replacement['start_at']).astimezone(timezone.utc).isoformat(),
                         'end_at':timestamp(replacement['end_at']).astimezone(timezone.utc).isoformat()}
        row={'project_id':self.project,'user_id':user_id,'interval_id':interval_id,
             'previous_revision':previous_revision,'action':action,'at':timestamp(when).astimezone(timezone.utc).isoformat(),
             'reason':reason,'replacement':replacement}
        row['revision_id']=digest(row)
        with self.ledger.connection() as db:
            with db:
                db.execute('BEGIN IMMEDIATE'); initialize(db)
                found=db.execute('SELECT payload FROM human_amendments WHERE revision_id=?',(row['revision_id'],)).fetchone()
                if found:
                    require(found[0]==encode(row),'Revision conflict')
                    return {'status':'duplicate','revision_id':row['revision_id']}
                originals=projected(db)
                original=next((r for r in originals if r['interval_id']==interval_id),None)
                require(original is not None,'Unknown interval')
                archived=db.execute('SELECT 1 FROM human_archive WHERE interval_id=?',(interval_id,)).fetchone()
                require(original['end_at'] is not None or archived,'Stop live timer before amending')
                states=effective(originals,amendments(db)+[row]); check_overlaps(states)
                db.execute('INSERT INTO human_amendments(revision_id,payload) VALUES(?,?)',(row['revision_id'],encode(row)))
        return {'status':'inserted','revision_id':row['revision_id']}

    def summary(self, user_id):
        from .human_history import snapshot
        rows=self.intervals(user_id); by_task={}; by_kind={}; count=0; opened=0; confirmed=0
        for row in rows:
            if row['voided']: continue
            if row['end_at'] is None:
                opened+=1; continue
            seconds=int((timestamp(row['end_at'])-timestamp(row['start_at'])).total_seconds())
            by_task[row['task_id']]=by_task.get(row['task_id'],0)+seconds
            by_kind[row['activity_kind']]=by_kind.get(row['activity_kind'],0)+seconds
            count+=1
            if row['confirmed']: confirmed+=seconds
        with self.ledger.connection() as db: warnings=snapshot(db,self.project)['warnings']
        return {'project_id':self.project,'user_id':user_id,'active_seconds':sum(by_task.values()),
                'by_task':by_task,'by_activity':by_kind,'closed_intervals':count,'open_intervals':opened,
                'complete':not opened and not warnings,'confirmed_seconds':confirmed,'warnings':warnings,
                'basis':'explicit_timer_not_attention_measurement','attention_verified':False,'unlogged_time':'unknown'}

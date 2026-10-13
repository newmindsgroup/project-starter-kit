# Version-Timestamp: 2026-10-13 08:14:00 AST
"""Scoped self-reported intervals and immutable amendment chains."""
import json
from .contracts import project_id, opaque, require, timestamp
from .ledger import digest, encode

KINDS = {'authoring','briefing','chatting','supervising','reviewing','rework'}
REASONS = {'timer_left_running','wrong_task','wrong_activity','duplicate','user_review','manual_reconciliation'}
INTERVAL_FIELDS = {'interval_id','project_id','user_id','task_id','activity_kind','start_at','end_at','source'}
AMEND_FIELDS = {'revision_id','project_id','user_id','interval_id','previous_revision','action','at','reason','replacement'}


def exists(db, table):
    return db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone() is not None


def initialize(db):
    db.execute('CREATE TABLE IF NOT EXISTS human_archive(interval_id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS human_amendments(seq INTEGER PRIMARY KEY,revision_id TEXT UNIQUE NOT NULL,payload TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS human_history_warnings(project_id TEXT NOT NULL,reason TEXT NOT NULL,PRIMARY KEY(project_id,reason))')


def validate_interval(row, identity):
    require(isinstance(row,dict) and set(row)==INTERVAL_FIELDS,'Invalid human interval')
    opaque(row['interval_id']); project_id(row['project_id']); project_id(row['user_id']); project_id(row['task_id'])
    require(row['project_id']==identity,'Cross-project history refused')
    require(isinstance(row['activity_kind'],str) and row['activity_kind'] in KINDS,'Invalid activity')
    require(row['source']=='explicit_timer','Invalid evidence basis')
    start=timestamp(row['start_at'])
    if row['end_at'] is not None:
        require(timestamp(row['end_at'])>=start,'Negative human interval')
    return row


def projected(db):
    intervals = {}
    if exists(db,'human_archive'):
        intervals.update((key,json.loads(raw)) for key,raw in db.execute('SELECT interval_id,payload FROM human_archive'))
    active = {}
    if exists(db,'human_transitions'):
        for event_id,raw in db.execute('SELECT event_id,payload FROM human_transitions ORDER BY seq'):
            row=json.loads(raw); user=row['user_id']
            previous=active.pop(user,None)
            if previous:
                previous['end_at']=row['timestamp']
            if row['action'] in {'start','resume','switch'}:
                interval={'interval_id':digest(['human-interval.v1',event_id,row['project_id'],user]),
                          'project_id':row['project_id'],'user_id':user,'task_id':row['task_id'],
                          'activity_kind':row['activity_kind'],'start_at':row['timestamp'],
                          'end_at':None,'source':'explicit_timer'}
                require(interval['interval_id'] not in intervals,'Interval identity conflicts')
                intervals[interval['interval_id']]=interval; active[user]=interval
    return list(intervals.values())


def amendments(db):
    return [json.loads(raw) for (raw,) in db.execute('SELECT payload FROM human_amendments ORDER BY seq')] if exists(db,'human_amendments') else []


def effective(intervals, changes):
    states={r['interval_id']:{**r,'revision_id':r['interval_id'],'confirmed':False,'voided':False} for r in intervals}
    seen=set()
    for change in changes:
        require(isinstance(change,dict) and set(change)==AMEND_FIELDS,'Invalid amendment')
        for key in ('revision_id','interval_id','previous_revision'): opaque(change[key])
        project_id(change['project_id']); project_id(change['user_id']); timestamp(change['at'])
        require(isinstance(change['reason'],str) and change['reason'] in REASONS,'Invalid amendment reason')
        require(change['revision_id']==digest({k:v for k,v in change.items() if k!='revision_id'}),'Amendment identity mismatch')
        require(change['revision_id'] not in seen,'Duplicate revision')
        seen.add(change['revision_id'])
        state=states.get(change['interval_id'])
        require(state is not None and state['project_id']==change['project_id'] and state['user_id']==change['user_id'],'Invalid amendment reference')
        require(state['revision_id']==change['previous_revision'],'Stale interval revision')
        require(timestamp(change['at'])>=timestamp(state.get('amended_at',state['start_at'])),'Amendment time regressed')
        action=change['action']; require(isinstance(action,str) and action in {'correct','confirm','void'},'Invalid amendment action')
        require(not state['voided'],'Voided interval is terminal')
        if action=='correct':
            replacement=change['replacement']
            require(isinstance(replacement,dict) and set(replacement)=={'task_id','activity_kind','start_at','end_at'},'Invalid correction fields')
            candidate={k:v for k,v in state.items() if k in INTERVAL_FIELDS}; candidate.update(replacement)
            validate_interval(candidate,state['project_id']); require(candidate['end_at'] is not None,'Correction requires closed interval')
            require(timestamp(candidate['end_at'])<=timestamp(change['at']),'Correction ends after recorded review')
            state.update(replacement); state['confirmed']=False
        else:
            require(change['replacement'] is None,'Unexpected replacement')
            if action=='confirm':
                require(state['end_at'] is not None and timestamp(state['end_at'])<=timestamp(change['at']),'Cannot confirm unresolved or future interval')
                state['confirmed']=True
            else: state['voided']=True; state['confirmed']=False
        state.update(revision_id=change['revision_id'],amended_at=change['at'])
    return list(states.values())


def check_overlaps(states):
    by_user={}
    for row in states:
        if not row['voided'] and row['end_at'] is not None:
            by_user.setdefault(row['user_id'],[]).append((timestamp(row['start_at']),timestamp(row['end_at'])))
    for spans in by_user.values():
        end=None
        for start,stop in sorted(spans):
            require(end is None or start>=end,'Overlaps existing human history')
            end=stop


def snapshot(db, identity):
    intervals=[r for r in projected(db) if r['project_id']==identity]
    changes=[r for r in amendments(db) if r['project_id']==identity]
    warnings=[r[0] for r in db.execute('SELECT reason FROM human_history_warnings WHERE project_id=?',(identity,))] if exists(db,'human_history_warnings') else []
    return {'intervals':intervals,'amendments':changes,'warnings':warnings}


def validate_history(history, identity):
    require(isinstance(history,dict) and set(history)=={'intervals','amendments','warnings'},'Invalid human history')
    require(isinstance(history['intervals'],list) and isinstance(history['amendments'],list) and isinstance(history['warnings'],list),'Invalid history lists')
    require(all(w=='human_history_not_in_backup' for w in history['warnings']) and len(history['warnings'])<=1,'Invalid history warning')
    ids=set()
    for row in history['intervals']:
        validate_interval(row,identity); require(row['interval_id'] not in ids,'Duplicate interval'); ids.add(row['interval_id'])
    states=effective(history['intervals'],history['amendments']); check_overlaps(states)
    return states


def load(db, history, identity):
    initialize(db)
    for row in history['intervals']:
        db.execute('INSERT INTO human_archive VALUES(?,?)',(row['interval_id'],encode(row)))
    for row in history['amendments']:
        db.execute('INSERT INTO human_amendments(revision_id,payload) VALUES(?,?)',(row['revision_id'],encode(row)))
    for warning in history['warnings']: db.execute('INSERT OR IGNORE INTO human_history_warnings VALUES(?,?)',(identity,warning))

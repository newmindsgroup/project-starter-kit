# Version-Timestamp: 2026-10-13 08:14:00 AST
"""Private transactional metadata ledger with exact replay and export checks."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from .contracts import opaque, project_id, require, validate_event


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


class Ledger:
    def __init__(self, path, read_only=False):
        self.path = Path(path).absolute()
        self.read_only = read_only
        require(os.name == 'posix', 'Private ledger requires POSIX permission support')
        require(not any(p.is_symlink() for p in (self.path, *self.path.parents)), 'Symlink storage refused')
        if read_only:
            require(self.path.is_file(), 'Ledger absent')
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        require(self.path.parent.stat().st_mode & 0o077 == 0, 'Choose a private storage directory')
        if self.path.exists():
            require(self.path.is_file(), 'Invalid ledger target')
            probe = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)
            try:
                require(probe.execute('PRAGMA application_id').fetchone()[0] == 0x50424C44,
                        'Unrecognized database; preserve original')
                require(probe.execute('PRAGMA user_version').fetchone()[0] == 1,
                        'Unsupported ledger version; preserve original')
            finally:
                probe.close()
            require(self.path.stat().st_mode & 0o077 == 0, 'Ledger permissions are not private')
        else:
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            os.close(fd)
        if read_only:
            return
        with self.connection() as db:
            version = db.execute('PRAGMA user_version').fetchone()[0]
            require(version in (0, 1), 'Unsupported ledger version; preserve original')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
                    project_id TEXT NOT NULL, task_id TEXT, session_id TEXT NOT NULL,
                    attempt_id TEXT NOT NULL, stream_key TEXT NOT NULL,
                    payload TEXT NOT NULL, effective TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS counters (
                    stream_key TEXT PRIMARY KEY, project_id TEXT NOT NULL,
                    identity TEXT NOT NULL, usage TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS cursors (
                    source_id TEXT PRIMARY KEY, generation TEXT NOT NULL, offset INTEGER NOT NULL);
                PRAGMA application_id=1346522180;
                PRAGMA user_version=1;
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True, timeout=10) if self.read_only else sqlite3.connect(self.path, timeout=10)
        try:
            if not self.read_only:
                db.execute('PRAGMA journal_mode=DELETE')
                db.execute('PRAGMA synchronous=FULL')
            yield db
        finally:
            db.close()

    def ingest(self, event):
        return self.ingest_batch([event], None)['results'][0]

    def ingest_batch(self, events: list, cursor: dict = None) -> dict:
        require(isinstance(events, list) and len(events) <= 10000, 'Invalid event batch')
        if cursor is not None:
            require(isinstance(cursor, dict) and set(cursor) == {'source_id', 'generation', 'offset'}, 'Invalid cursor')
            opaque(cursor['source_id']); opaque(cursor['generation'])
            require(type(cursor['offset']) is int and 0 <= cursor['offset'] < 2**63, 'Invalid cursor offset')
        results = []
        with self.connection() as db:
            with db:
                db.execute('BEGIN IMMEDIATE')
                for event in events:
                    row = validate_event(event)
                    payload = encode(row)
                    old = db.execute('SELECT payload FROM events WHERE event_id=?', (row['event_id'],)).fetchone()
                    if old:
                        require(old[0] == payload, 'Event identity conflicts with persisted metadata')
                        results.append({'status': 'duplicate'})
                        continue
                    key = digest([row['machine_id'], row['provider'], row['stream_id']])
                    identity = encode([row['session_id'], row['usage_semantics'], row['usage_mode'], row['model']])
                    previous = db.execute('SELECT project_id,identity,usage FROM counters WHERE stream_key=?', (key,)).fetchone()
                    if previous:
                        require(previous[0] == row['project_id'] and previous[1] == identity, 'Stream ownership or semantics changed')
                    effective = dict(row['usage'])
                    if row['usage_mode'] == 'cumulative' and previous:
                        prior = json.loads(previous[2])
                        for name, value in row['usage'].items():
                            baseline = prior[name]
                            if value is not None and baseline is not None:
                                require(value >= baseline, 'Counter regressed; resolve source generation')
                                effective[name] = value - baseline
                            else:
                                effective[name] = None
                    db.execute('INSERT INTO events(event_id,project_id,task_id,session_id,attempt_id,stream_key,payload,effective) VALUES(?,?,?,?,?,?,?,?)',
                               (row['event_id'], row['project_id'], row['task_id'], row['session_id'], row['attempt_id'], key, payload, encode(effective)))
                    db.execute('INSERT INTO counters VALUES(?,?,?,?) ON CONFLICT(stream_key) DO UPDATE SET usage=excluded.usage',
                               (key, row['project_id'], identity, encode(row['usage'])))
                    results.append({'status': 'inserted'})
                if cursor is not None:
                    prior = db.execute('SELECT generation,offset FROM cursors WHERE source_id=?', (cursor['source_id'],)).fetchone()
                    require(not prior or prior[0] != cursor['generation'] or cursor['offset'] >= prior[1], 'Cursor regressed within source generation')
                    db.execute('INSERT INTO cursors VALUES(?,?,?) ON CONFLICT(source_id) DO UPDATE SET generation=excluded.generation,offset=excluded.offset',
                               (cursor['source_id'], cursor['generation'], cursor['offset']))
        return {'results': results, 'cursor_committed': cursor is not None}

    def query(self, identity: str, filters: dict) -> list:
        project_id(identity)
        require(isinstance(filters, dict) and set(filters) <= {'task_id', 'session_id', 'attempt_id'}, 'Unsupported filter')
        clauses = ['project_id=?']; args = [identity]
        for key, value in filters.items():
            if key == 'task_id': project_id(value)
            else: opaque(value)
            clauses.append(key + '=?'); args.append(value)
        with self.connection() as db:
            rows = db.execute('SELECT payload,effective FROM events WHERE ' + ' AND '.join(clauses) + ' ORDER BY seq', args).fetchall()
        return [{**json.loads(raw), 'effective_usage': json.loads(effective)} for raw, effective in rows]

    def cursor(self, source_id):
        opaque(source_id)
        with self.connection() as db:
            row = db.execute('SELECT generation,offset FROM cursors WHERE source_id=?', (source_id,)).fetchone()
        return None if row is None else {'source_id': source_id, 'generation': row[0], 'offset': row[1]}

    def export(self, identity):
        rows = self.query(identity, {})
        packet = {'schema': 'blueprint-export.v1', 'project_id': identity,
                  'events': [{k: v for k, v in row.items() if k != 'effective_usage'} for row in rows]}
        return {**packet, 'sha256': digest(packet)}

    def export_history(self, identity):
        from .human_history import snapshot, validate_history
        project_id(identity)
        with self.connection() as db:
            db.execute('BEGIN')
            events=[json.loads(raw) for (raw,) in db.execute('SELECT payload FROM events WHERE project_id=? ORDER BY seq',(identity,))]
            human=snapshot(db,identity); validate_history(human,identity)
        packet={'schema':'blueprint-export.v2','project_id':identity,'events':events,'human':human}
        return {**packet,'sha256':digest(packet)}

    @classmethod
    def restore(cls, path, packet):
        from .human_history import validate_history, load
        import uuid
        require(isinstance(packet,dict), 'Invalid export')
        version=packet.get('schema')
        require(version in ('blueprint-export.v1','blueprint-export.v2'),'Unsupported export')
        require(set(packet)==({'schema','project_id','events','sha256','human'} if version=='blueprint-export.v2' else {'schema','project_id','events','sha256'}),'Invalid export')
        body = {k: v for k, v in packet.items() if k != 'sha256'}
        require(digest(body) == packet['sha256'], 'Export integrity check failed')
        project_id(packet['project_id'])
        require(isinstance(packet['events'], list), 'Invalid export events')
        for event in packet['events']:
            validate_event(event)
            require(event['project_id'] == packet['project_id'], 'Cross-project export refused')
        history=packet['human'] if version=='blueprint-export.v2' else {'intervals':[],'amendments':[],'warnings':['human_history_not_in_backup']}
        validate_history(history,packet['project_id'])
        target=Path(path).absolute()
        require(not target.exists() and not target.is_symlink(),'Restore is create-only')
        staging=target.with_name('restore-'+uuid.uuid4().hex+'.db')
        ledger=None
        try:
            ledger=cls(staging)
            for offset in range(0,len(packet['events']),10000):
                ledger.ingest_batch(packet['events'][offset:offset+10000])
            with ledger.connection() as db:
                with db: load(db,history,packet['project_id'])
            os.link(staging,target)
        finally:
            if ledger is not None and staging.exists(): staging.unlink()
        return cls(target)

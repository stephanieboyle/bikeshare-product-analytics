"""Append-only metadata and status observations; one process at a time."""
import fcntl
import hashlib
import json
import logging
import time
from pathlib import Path

import duckdb

from .io import DISCOVERY, atomic, fetch_json, now, session

LOG = logging.getLogger(__name__)
REQUIRED = ['station_id', 'num_bikes_available', 'num_docks_available', 'is_installed',
            'is_renting', 'is_returning', 'last_reported']


def validate_stations(d, status=True):
    rows = d['data']['stations']
    ids = [x['station_id'] for x in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError('Empty or duplicate station list')
    for r in rows:
        for k in (REQUIRED if status else ['station_id', 'name', 'short_name', 'lat', 'lon', 'capacity']):
            if k not in r:
                raise ValueError(f'Missing station field: {k}')
        if status:
            for k in ['num_bikes_available', 'num_docks_available', 'last_reported']:
                if not isinstance(r[k], int) or isinstance(r[k], bool) or r[k] < 0:
                    raise ValueError(f'Invalid {k}')
            for k in ['is_installed', 'is_renting', 'is_returning']:
                if r[k] not in (0, 1):
                    raise ValueError(f'Invalid operational flag {k}')
            types = r.get('vehicle_types_available', [])
            if len({x['vehicle_type_id'] for x in types}) != len(types):
                raise ValueError('Duplicate vehicle type')
            if any(not isinstance(x['count'], int) or x['count'] < 0 for x in types):
                raise ValueError('Invalid vehicle-type count')
    return rows


def init_db(db):
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    c = duckdb.connect(str(db))
    c.execute('''create table if not exists live_status (
      station_id varchar, retrieved double, feed_time bigint, last_reported bigint,
      bikes integer, docks integer, installed boolean, renting boolean, accepting_returns boolean,
      types_json varchar, snapshot_id varchar, primary key(station_id, snapshot_id))''')
    c.execute('''create table if not exists station_metadata (
      snapshot_id varchar primary key, retrieved double, feed_time bigint, payload varchar)''')
    c.execute('''create table if not exists collection_runs (
      started double, finished double, success boolean, message varchar)''')
    return c


def collect_once(db='data/bikeshare.duckdb', root=Path('data/raw/gbfs')):
    started = now().timestamp()
    c = init_db(db)
    try:
        with session() as s:
            discovery, _ = fetch_json(s, DISCOVERY)
            urls = {x['name']: x['url'] for x in discovery['data']['en']['feeds']}
            docs = {}
            retrieved = {}
            for name in ['station_information', 'station_status', 'system_information', 'vehicle_types']:
                docs[name], retrieved[name] = fetch_json(s, urls[name])
            for name in ['system_hours', 'system_calendar', 'system_alerts']:
                if name in urls:
                    docs[name], retrieved[name] = fetch_json(s, urls[name])
        info = validate_stations(docs['station_information'], False)
        status = validate_stations(docs['station_status'])
        body = json.dumps({'sources': urls, 'retrieved': retrieved, 'feeds': docs}, sort_keys=True)
        sid = hashlib.sha256(body.encode()).hexdigest()
        atomic(root / f'{sid}.json', body.encode())
        # Freeze the initial universe, including closed stations. Never select on availability.
        universe = Path(db).parent / 'raw/monitored_universe.json'
        if not universe.exists():
            atomic(universe, json.dumps({'defined_at': retrieved['station_information'],
                   'rule': 'all station_information IDs at first collection',
                   'stations': sorted(x['station_id'] for x in info)}, indent=2).encode())
        c.execute('begin')
        c.execute('insert or ignore into station_metadata values (?, ?, ?, ?)',
                  [sid, retrieved['station_information'], docs['station_information']['last_updated'],
                   json.dumps(docs['station_information'])])
        c.executemany('insert or ignore into live_status values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      [(r['station_id'], retrieved['station_status'], docs['station_status']['last_updated'],
                        r['last_reported'], r['num_bikes_available'], r['num_docks_available'],
                        bool(r['is_installed']), bool(r['is_renting']), bool(r['is_returning']),
                        json.dumps(r.get('vehicle_types_available', [])), sid) for r in status])
        c.execute('insert into collection_runs values (?, ?, true, ?)', [started, now().timestamp(), sid])
        c.execute('commit')
        ttl = max(60, *(d['ttl'] for d in docs.values()))
        LOG.info('Collected %s station statuses, ttl floor %ss', len(status), ttl)
        return ttl
    except Exception as e:
        try:
            c.execute('rollback')
        except duckdb.TransactionException:
            pass
        c.execute('insert into collection_runs values (?, ?, false, ?)',
                  [started, now().timestamp(), str(e)[:500]])
        raise
    finally:
        c.close()


def collect(db, count=1, interval=120):
    if count < 1 or interval < 60:
        raise ValueError('count >= 1 and interval >= 60 required')
    lock = Path(db).parent / 'collection.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open('w') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        deadline = Path(db).parent / 'raw/next_request.json'
        for i in range(count):
            remaining = 0
            if deadline.exists():
                remaining = json.loads(deadline.read_text())['not_before'] - now().timestamp()
            if remaining > 0:
                if count == 1:
                    LOG.info('Skipping: prior TTL/poll deadline has %.1fs remaining', remaining)
                    return
                time.sleep(remaining)
            # Set a backoff floor even if a request fails. Successful feeds can increase it.
            atomic(deadline, json.dumps({'not_before': now().timestamp() + interval}).encode())
            ttl = collect_once(db)
            atomic(deadline, json.dumps({'not_before': now().timestamp() + max(interval, ttl)}).encode())

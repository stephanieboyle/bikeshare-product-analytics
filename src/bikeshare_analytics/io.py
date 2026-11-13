"""Bounded network requests and local, atomic source cache (not redistributed)."""
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LOG = logging.getLogger(__name__)
DISCOVERY = 'https://gbfs.lyft.com/gbfs/2.3/dca-cabi/gbfs.json'
TRIPS = 'https://s3.amazonaws.com/capitalbikeshare-data/{month}-capitalbikeshare-tripdata.zip'


def now():
    return datetime.now(timezone.utc)


def session():
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=['GET'], respect_retry_after_header=True)
    s.mount('https://', HTTPAdapter(max_retries=retry))
    s.headers['User-Agent'] = 'independent-bikeshare-portfolio/0.1 (non-commercial research)'
    return s


def atomic(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(content)
    os.replace(tmp, path)


def fetch_json(s, url):
    r = s.get(url, timeout=(10, 45))
    r.raise_for_status()
    d = r.json()
    if d.get('version') != '2.3' or not isinstance(d.get('data'), dict):
        raise ValueError(f'Unexpected GBFS envelope at {url}')
    if not isinstance(d.get('last_updated'), int) or not isinstance(d.get('ttl'), int):
        raise ValueError('Missing feed timestamp or ttl')
    return d, now().timestamp()


def download(month, raw=Path('data/raw')):
    import re
    if not re.fullmatch(r'20\d{2}(0[1-9]|1[0-2])', month):
        raise ValueError('month must be YYYYMM')
    path = raw / f'{month}.zip'
    manifest = path.with_suffix('.provenance.json')
    if path.exists() and manifest.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest() != json.loads(manifest.read_text())['sha256']:
            raise ValueError('Cached archive hash mismatch; remove corrupt cache and retry')
        return path
    url = TRIPS.format(month=month)
    with session() as s:
        r = s.get(url, timeout=(10, 120))
        r.raise_for_status()
    atomic(path, r.content)
    atomic(manifest, json.dumps({'url': url, 'retrieved_at': now().isoformat(),
           'sha256': hashlib.sha256(r.content).hexdigest(), 'bytes': len(r.content)}, indent=2).encode())
    LOG.info('Downloaded %s (%s bytes)', month, len(r.content))
    return path

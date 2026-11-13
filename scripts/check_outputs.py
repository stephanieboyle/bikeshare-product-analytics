"""Offline checks of committed aggregate evidence, not a replay of source data."""
import json
from pathlib import Path

from PIL import Image

s = json.loads(Path('reports/summary.json').read_text())
assert s['full_month_ingestion'], 'Do not publish feasibility rows as complete-period findings'
assert s['conflicting_ride_ids'] == 0
assert len(s['months']) == 3
assert sum(x['n'] for x in s['months']) > 0
p = json.loads(Path('reports/pilot_summary.json').read_text())
assert p['horizon_seconds'] < 86400, 'Update pilot narrative when collection matures'
for m in p.get('sensitivity', []):
    for key in ['coverage', 'time_weighted_availability', 'equal_station_availability']:
        assert 0 <= m[key] <= 1
sim = json.loads(Path('reports/simulation.json').read_text())
assert sim['evidence_class'].startswith('SYNTHETIC')
assert sim['repetitions'] >= 2000
# Broad MC-aware correctness gates, not a requirement to hit nominal rates exactly.
for key in ['null', 'user_mean_robust_NULL']:
    x = sim['scenarios'][key]
    assert abs(x['rejection_rate'] - .05) < 4 * (x['rejection_mc_se'] + .001)
assert abs(sim['scenarios']['plausible_effect']['bias']) < .002
figs = list(Path('reports/figures').glob('*.png'))
assert 4 <= len(figs) <= 6
for f in figs:
    with Image.open(f) as im:
        im.verify()
print(f'Aggregate evidence checks passed; {len(figs)} readable figures. Source re-extraction needs network.')

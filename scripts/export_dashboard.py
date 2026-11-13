"""Export only aggregate analytical cells; no raw trip records or user identifiers."""
import calendar
import json
import sys
from pathlib import Path

import duckdb

root = Path(__file__).resolve().parents[1]
out = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'dashboard/data.json'
out.parent.mkdir(parents=True, exist_ok=True)
c = duckdb.connect(str(root / 'data/bikeshare.duckdb'), read_only=True)
queries = {
 'daily': '''select strftime(start_local,'%Y-%m-%d') as day, analysis_month as month,
 rideable_type bike, member_casual rider, count(*) n,
 count(*) filter(where departure_station_code is null) missing_start,
 count(*) filter(where arrival_station_code is null) missing_end
 from fct_trips group by all order by 1,3,4''',
 'hourly': '''select analysis_month as month, extract(isodow from start_local)::int dow,
 extract(hour from start_local)::int as hour, rideable_type bike, member_casual rider, count(*) n
 from fct_trips group by all''',
 'stations': '''with dep as (select analysis_month as month, departure_station_code code,
 rideable_type bike, member_casual rider, max(start_station_name) as name, count(*) departures,
 count(*) filter(where extract(isodow from start_local)<=5 and
 (extract(hour from start_local) between 7 and 9 or extract(hour from start_local) between 16 and 18)) core,
 count(*) filter(where extract(isodow from start_local)<=5 and
 (extract(hour from start_local) between 6 and 9 or extract(hour from start_local) between 15 and 19)) wide
 from fct_trips where departure_station_code is not null group by all),
 arr as (select analysis_month as month, arrival_station_code code, rideable_type bike, member_casual rider,
 max(end_station_name) as name, count(*) arrivals from fct_trips
 where arrival_station_code is not null group by all)
 select coalesce(d.month,a.month) as month, coalesce(d.code,a.code) code,
 coalesce(d.bike,a.bike) bike, coalesce(d.rider,a.rider) rider, coalesce(d.name,a.name) as name,
 coalesce(departures,0) departures, coalesce(arrivals,0) arrivals, coalesce(core,0) core,
 coalesce(wide,0) wide from dep d full outer join arr a using(month,code,bike,rider)'''
}
data = {key: c.sql(query).df().to_dict('records') for key, query in queries.items()}
for key, filename in [('summary','summary'),('pilot','pilot_summary'),('simulation','simulation')]:
 data[key] = json.loads((root / f'reports/{filename}.json').read_text())
data['calendar'] = {str(m): [sum(1 for day in calendar.Calendar().itermonthdates(2026,m)
 if day.month==m and day.isoweekday()==dow) for dow in range(1,8)] for m in [8,9,10]}
assert sum(r['n'] for r in data['daily']) == sum(x['n'] for x in data['summary']['months'])
assert sum(r['n'] for r in data['hourly']) == sum(r['n'] for r in data['daily'])
assert sum(r['departures'] for r in data['stations']) == sum(r['n']-r['missing_start'] for r in data['daily'])
assert sum(r['arrivals'] for r in data['stations']) == sum(r['n']-r['missing_end'] for r in data['daily'])
out.write_text(json.dumps(data, separators=(',', ':'), allow_nan=False))
print(f'Exported reconciled aggregate cells to {out} ({out.stat().st_size:,} bytes)')
c.close()

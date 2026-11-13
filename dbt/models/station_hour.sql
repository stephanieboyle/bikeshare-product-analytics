-- Grain: start month x weekday (0=Sunday) x local hour x departure station code.
select analysis_month, extract(dow from start_local)::integer as weekday,
 extract(hour from start_local)::integer as local_hour, departure_station_code,
 count(*) as completed_departures
from {{ ref('fct_trips') }} where departure_station_code is not null
group by all

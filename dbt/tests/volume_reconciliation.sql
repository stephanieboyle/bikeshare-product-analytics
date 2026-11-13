select 1 where
 (select sum(completed_departures) from {{ ref('station_hour') }}) !=
 (select count(*) from {{ ref('fct_trips') }} where departure_station_code is not null)

select source_month, weekday, local_hour, departure_station_code
from {{ ref('station_hour') }} group by all having count(*) > 1

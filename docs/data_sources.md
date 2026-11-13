# Sources, access and feasibility

Verified 13 November 2026 through the official pages and direct responses. Exact extraction timestamps and SHA-256 hashes are in local `data/raw/*.provenance.json`; feed retrieval timestamps are in each local response bundle. Public aggregate outputs credit Capital Bikeshare. This is an independent, non-commercial portfolio study with no operator affiliation or endorsement. No logos are used.

| Source | Exact link | Verified use |
|---|---|---|
| Official data entry point | https://capitalbikeshare.com/system-data | Monthly trips and live feed links; prose describes an older schema, updated December 2016 |
| Data licence | https://capitalbikeshare.com/data-license-agreement | Access and analysis permitted; standalone dataset redistribution restricted |
| Official trip archive | https://s3.amazonaws.com/capitalbikeshare-data/index.html | Authorised download interface linked from official page |
| August CSV archive | https://s3.amazonaws.com/capitalbikeshare-data/202608-capitalbikeshare-tripdata.zip | Complete month |
| September CSV archive | https://s3.amazonaws.com/capitalbikeshare-data/202609-capitalbikeshare-tripdata.zip | Complete month |
| October CSV archive | https://s3.amazonaws.com/capitalbikeshare-data/202610-capitalbikeshare-tripdata.zip | First feasibility inspection; complete month then ingested |
| Official discovery entry point | https://gbfs.capitalbikeshare.com/gbfs/gbfs.json | Linked on official data page |
| Versioned discovery used | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/gbfs.json | Responds with GBFS 2.3, English and other language feeds |
| Station information | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/station_information.json | IDs, short codes, name, lat/lon, capacity |
| Station status | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/station_status.json | Bikes, docks, flags, last reporting, type counts |
| System information | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/system_information.json | America/New_York; no licence field in inspected response |
| Vehicle definitions | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/vehicle_types.json | Type 1: human bicycle; type 2: electric-assist bicycle |
| Operating hours | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/system_hours.json | Empty rental_hours in inspected response; not evidence of an individual closure |
| Calendar | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/system_calendar.json | Saved with snapshots where discoverable |
| Alerts | https://gbfs.lyft.com/gbfs/2.3/dca-cabi/en/system_alerts.json | Saved for later closure/context review |
| Version-specific standard | https://github.com/MobilityData/gbfs/blob/v2.3/gbfs.md | Envelope, latency, reporting and TTL semantics |
| Operator product help | https://help.capitalbikeshare.com/hc/en-us/articles/360039401851-How-to-end-a-bike-ride | App shows exact bike/dock counts; classic and electric bikes can dock; ebike rack return also possible |
| Operator station help | https://help.capitalbikeshare.com/hc/en-us/articles/360039403211-What-is-a-station-A-dock-A-kiosk | Existing map availability; broken docks and temporary deactivation |

## Permissions and request discipline

The operator licence permits analysis and inclusion of source material in non-commercial analyses, reports and studies, but prohibits distributing the data as a standalone dataset. It also restricts website extraction, bypassing access controls, customer re-identification and implied affiliation or unauthorised marks. This project uses the explicitly provided monthly archives and GBFS interfaces, never website scraping or customer matching. Raw data and station-level extracts stay local and ignored. No broad open-data licence is inferred from a third-party catalogue; the inspected system response has no `license_id` or `license_url`. Check terms again before reuse, commercialisation or publication.

No separate numerical operator request quota was found on the official data page or in inspected responses. GBFS 2.3 says near-real-time reports should be no more than five minutes old; this is a producer recommendation, not an observed guarantee. Responses advertised `ttl=60` seconds. Poll defaults to 120 seconds, never below 60 or the largest advertised TTL across requested feeds. HTTP 429 Retry-After and bounded retries are honoured. Historical archives are locally cached with hash checks; no caching prohibition was found in the reviewed licence. A network timeout applies to each request; three retries bound retry count (a server Retry-After may extend elapsed time).

## Actual schema, not website assumptions

Trips (13 fields): `ride_id`, `rideable_type`, `started_at`, `ended_at`, `start_station_name`, `start_station_id`, `end_station_name`, `end_station_id`, `start_lat`, `start_lng`, `end_lat`, `end_lng`, `member_casual`. IDs are strings even when numeric-looking. Timestamps include fractional seconds and have no offset; local operating time is an explicit assumption, verified for plausible behavioural interpretation, not a publisher guarantee in the CSV header. Preserve the original strings and derived UTC instants. There is no stable rider ID. The archive has one CSV per tested month and a consistent header. Older archives may differ; unexpected headers fail rather than silently coerce.

GBFS station metadata includes `station_id`, `short_name`, `name`, `lat`, `lon`, `capacity`, `rental_uris` and `is_charging`, with optional `region_id`. Status includes `num_bikes_available`, `num_bikes_disabled`, `num_docks_available`, `num_docks_disabled`, `is_installed`, `is_renting`, `is_returning`, `last_reported`, `vehicle_types_available`, plus producer extensions such as `num_ebikes_available`. Envelope `last_updated`, `ttl`, `version` are present. Real responses use 0/1 operational flags despite the standard's boolean type; the collector accepts both and stores booleans. It is a focused consumer validator, not a claim of full GBFS conformance certification.

Trip station codes correspond to GBFS `short_name`, not `station_id` (which includes UUID and numeric formats). Mapping uniqueness is checked; unmatched codes and their trip counts are reported. A current crosswalk cannot establish past capacity, past station location or permanent identity over time. Metadata is saved per collection rather than overwritten. No historical capacity is joined to trips.

## Feasibility boundary

The October ZIP was inspected first (32,848,117 bytes), including actual header and one record. A 1,000-row ingestion verified the pipeline; it was replaced with the complete month before published historical analysis. August and September ZIPs were approximately 24 MB and 26 MB. The three full months are manageable locally.

The official sources reviewed publish historical **trips** and **current station state**. No operator-published historical station-status archive was identified through these official sources. This does not establish that no third party has an archive. We do not switch operators or reconstruct stock from trip flow. Historical timing, rental mix and station departures are answerable now; stockouts, their duration, fresh-information coverage and their recurrence require prospective snapshots. Attempted journeys and feature effects need operator instrumentation or research beyond these public feeds.

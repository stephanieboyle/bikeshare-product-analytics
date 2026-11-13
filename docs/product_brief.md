# Product brief

## Rider and journey

Target a rider who already has a regular weekday journey and is willing to save departure and arrival station preferences. A concrete need: leave home around 08:15, find a suitable bike within a tolerable walk and return it near work without an unexpected detour. This is a proposed user segment; membership labels do not identify it in public trips. Validate the need with riders before treating it as prevalent.

Reliability has four separate layers:

1. **Physical service:** a rentable bike of the acceptable type at departure and a usable docking option at arrival, while the station is operating.
2. **Information:** counts are recent enough, reflect closures and distinguish unknown from empty. Information can deteriorate while a rider walks.
3. **Decisions:** a rider can choose a suitable alternative within their walking, price and accessibility constraints.
4. **Journey:** rental starts and return completes within the rider's needs. A station count does not measure this outcome.

## Opportunity and existing functionality

The operator's public help already describes viewing exact bike and dock counts on the app map and switching the map to docks (see linked sources in `data_sources.md`). Therefore a map with counts is not a novel proposal. The reviewed public information does not settle current favourites, alert or alternative-station functionality; absence from a help page is not absence from the app. A hands-on audit and operator discussion are prerequisites to specification.

Test a **saved commute check**: the rider confirms “I plan to leave in the next 15 minutes”, then sees a combined departure/arrival check, report age and a small number of nearby alternatives, with optional explicitly requested reminders. Respect acceptable bicycle type, walking limit, price and notification permissions. Do not promise inventory on arrival or imply reservation. If reports are stale, show “status unavailable” rather than a confident recommendation. Destination counts are current, not predictions for return time.

The difference to evaluate is less effort and better decisions at the right journey moment, on top of the existing map. The core trial tests the in-app check first; scheduled alerts are a later extension requiring separate pre-intent eligibility and delivery design.

## Evidence and limits

Completed trips identify served volume, time patterns and candidate places to investigate. Live status can describe capped observed operating time and information freshness in a frozen station universe. Neither identifies a failed attempt, a rider's intent or willingness to walk. Current metadata cannot supply historical capacity. Initial snapshots validate collection mechanics only. User research must establish whether riders want this check and whether alternative options are acceptable.

The feature redistributes decisions; it does not create bikes or docks. Persistent failures across nearby alternatives would favour rebalancing or capacity work. Sustainability is a motivation, not a measured outcome: extra rides do not establish avoided car trips or reduced lifecycle emissions.

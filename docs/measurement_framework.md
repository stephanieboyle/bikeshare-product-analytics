# Measurement framework

## Universe and temporal support

Freeze all station_information IDs from the first collector run, without selecting on availability. Local `data/raw/monitored_universe.json` records IDs and definition time. This is the initial monitored cohort, not every station ever operated. New stations require a separately dated cohort; removed stations remain in the original cohort until a documented eligibility change, rather than silently disappearing. No historical-trip subset selects the live sample.

Use half-open intervals in UTC seconds. For retrieval time r, next retrieval n, station report s, feed time f, horizon end H, maximum hold h and freshness F:

`right = min(n, r+h, s+F, f+F, H)`; `left = max(r, horizon_start)`.

Only non-negative report and feed ages at retrieval, both ≤F, can contribute. Interval length is `max(0, right-left)`. Defaults F=300s, h=180s, polling=120s. The final observation contributes only up to explicit horizon end; the pilot report sets that end to the last retrieval, avoiding unobserved future time. A fresh HTTP result alone is insufficient. Polling misses changes within an interval; these are capped estimates of state support, not continuous observation.

For each station i and direction k, define Eᵢ = horizon seconds minus **fresh, bounded, observed closed seconds** for that direction. Default expected schedule is 24 hours/day; the inspected hours feed is empty, so this is a documented monitoring assumption, not a complete verified station calendar. Closures beyond observed support and unexplained missing stations stay unknown, within Eᵢ. Known closures do not count as stockouts. Missingness may correlate with service problems, so conditional availability alone is insufficient.

## Metrics

| Metric | Formula and unit | Denominator / caveat |
|---|---|---|
| Departure availability | Σ valid interval seconds × I(rentable bikes of acceptable type ≥b) / Σ valid departure seconds; % | Installed and renting; fresh; known count. Default b=1. All-bike metric means either type acceptable. Type 1 and type 2 can be evaluated separately; missing type is unknown, not zero |
| Arrival dock availability | Σ valid interval seconds × I(usable docks ≥d) / Σ valid arrival seconds; % | Installed and accepting returns; fresh; d=1. Measures docking only. Ebike rack return is a distinct option, so zero docks is not necessarily failed ebike return |
| Data coverage | Σ valid seconds / Eᵢ; % | Direction-specific; missing/stale time is not successful or failed availability. All-closed horizon has undefined coverage and availability |
| Observed zero run | Consecutive connected valid intervals with count=0; supported seconds and run count | Split at gaps and closures. True start/end lie between polls or outside the horizon; separate runs across a gap may be one true episode. No claim of exact frequency or duration |
| Information freshness | retrieval − last_reported; seconds, median/p95 and share >F or future dated | Raw station-observation denominator; report feed age separately. Poll frequency affects observation-weighting |
| Closure support | Σ fresh bounded closed seconds; station-seconds | Report separately so conditional availability does not hide loss of service |

`summary.json` describes historical trip denominators and exclusions, including archive/start/end-month boundary counts. `pilot_summary.json` contains descriptive technical pilot aggregates and sensitivity results. No metric here is a rider success probability; departure and arrival ratios must not be multiplied to invent journey completion.

## Weighting and selection

- Equal-station mean: arithmetic mean of defined station ratios, reporting count of eligible and undefined stations. It answers what a typical measured station ratio is.
- Station-time mean: Σ available seconds / Σ valid seconds. Stations with more observed operating time receive more weight. Pooled coverage is Σ valid seconds / Σ expected eligible seconds.
- Historical-trip-weighted mean: Σ wᵢAᵢ / Σ wᵢ for matched, measured stations; weights are complete-period departures, fixed before prospective outcomes. It represents previously **served trips**, not attempted or total demand. Always report unmatched trip weight, missing-outcome weight and coverage. Suppressed demand could be underweighted. The generic weighting function is tested, but this pilot does not publish a demand-weighted reliability claim.

## Planned decision analysis and sensitivity

Once collection matures, prioritise station/window effects of operational size, not a table of p-values. Compare b,d=1 versus 2; F=180/300/600s; hold=120/180s; 120s polling versus a separately labelled coarser subsample; core weekday windows [07:00,10:00) and [16:00,19:00) versus [06:00,10:00) and [15:00,20:00); coverage inclusion at 80/90/95%. Recompute rather than transfer rankings between definitions. Current reports implement freshness/hold/count sensitivities, equal versus time weighting, 80% coverage counts, and historical commute-window selection sensitivity. Interval-subsampling and mature station-window rankings remain future work, not completed findings.

For a mature descriptive report, split intervals at local-day/window boundaries, allocate actual UTC seconds, and use station-day windows as repeated units. Show dates with repeated problems and alternative-station context. Freeze analysis windows before viewing rankings. Fixed-period ratios are exact summaries of the supported intervals under the stated carry rule, not estimates with independent-snapshot binomial error bars. Future-period inference needs many more observed days; see methodology.

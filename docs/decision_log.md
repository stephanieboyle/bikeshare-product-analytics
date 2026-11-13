# Decision log

| Date | Choice | Reason and consequence |
|---|---|---|
| 2026-11-13 | Retain the initial operator candidate | Official archives and GBFS are accessible; no material feasibility reason to switch |
| 2026-11-13 | Keep raw source data and databases local | Standalone redistribution restriction; reproducible direct downloader rather than vendored source files |
| 2026-11-13 | August–October 2026, all rows | Three recent complete months with matching actual headers and modest ZIP sizes. First 1,000 October records were feasibility only, then replaced |
| 2026-11-13 | Preserve IDs as strings | Numeric inference can alter identifiers; GBFS station ID differs from trip station code |
| 2026-11-13 | Exclude unresolved local times and >24h/nonpositive durations | Avoid invented DST offsets and extreme-duration distortions. Audit impact rather than treating exclusions as bad users |
| 2026-11-13 | Keep subminute positive trips | Current files contain them despite older official descriptive text; no automatic removal based on stale prose |
| 2026-11-13 | Keep missing-station trips in aggregate counts | Missingness is substantial; deleting them globally would undercount completed rentals and distort mix |
| 2026-11-13 | Treat historical activity as served demand | Volumes, labels and net flow cannot identify stockouts, commuters, tourists or attempts |
| 2026-11-13 | Freeze all first-run station IDs | Avoid selecting monitored stations on good availability; record new station cohorts separately |
| 2026-11-13 | Five-minute freshness and three-minute maximum hold | Explicit bounded support; both feed and report times matter. TTL is request guidance, not a guarantee of freshness |
| 2026-11-13 | Separate closures, staleness, unknown and zero | A closed or unobserved station must not become a stockout or a success |
| 2026-11-13 | Existing counts are the comparison baseline | Public product help confirms map counts. Validate saved-pair workflow and alerts through audit/research rather than assume absence |
| 2026-11-13 | First-intent account ITT as initial experiment target | Avoid treatment-induced repeat-intent weighting and post-engagement selection. Estimate own-assignment benefit at trial saturation; no full-rollout effect claim |
| 2026-11-13 | Numeric user power is conditional planning only | No real intent success baseline or network dependence estimate. A cluster/switchback needs a separate calibrated design and power model |
| 2026-11-13 | Synthetic diagnostics in separate files | Demonstrate statistical implementation without suggesting an operator experiment or observed benefit |
| 2026-11-13 | No dashboard, public publication or unattended days-long session | Prioritise validated analysis; supply scheduling instructions and evidence-maturity gates |
| 2026-11-13 | Correct archive-month versus actual-start-month cohort | Boundary audit found August-start rentals in September's archive. Changed eligibility to the selected actual start-month set, retaining within-period boundary rentals and grouping by actual start month. Keep source month solely for provenance; document differing boundary patterns across archives |
| 2026-11-13 | Add an interactive reporting app after analytical validation | Owner explicitly requested a dashboard. Static aggregate cells reconcile to the validated fact model; historical, prospective and synthetic evidence remain distinct |
| 2026-11-13 | Warm dusty-blue, rose-pink and cream/peach palette | Owner rejected the initial green and cool indigo palettes; applied the warmer preference across charts, navigation and evidence labels |
| 2026-11-13 | Use a plainer, first-person voice | Owner asked for the app to sound more like them. Replaced formal portfolio language with what I looked at, found, still need to check and would try next; kept the statistical definitions and evidence limits |

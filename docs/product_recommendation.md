# What I’d try next: make a regular journey easier to check

**My next step, as of 13 November 2026:** talk to riders, check what the current app already does, and test whether the necessary tracking works. Do not claim that availability is consistently poor at named stations or that this feature will improve journeys. Historical analysis is complete for the selected published files; prospective collection is a technical sample, not mature service evidence.

## What the rider needs

A regular-journey rider needs to know whether a suitable bike is likely to be obtainable now and whether returning it near the destination is practical. A useful product should reduce avoidable uncertainty and wasted walking, while being candid about how quickly inventory changes. Physical supply and information are different problems: showing a better alternative may help one rider without adding bikes, docks or overall capacity.

The idea I’d test is a saved-journey check. It combines a rider's chosen departure and arrival stations, acceptable bicycle types and walking limit. After a neutral confirmation of imminent departure intent, show fresh counts, report age, operating flags and a small set of suitable alternatives. Do not imply a reservation or predict destination inventory from the current count. Optional reminders would be a subsequent scope, with independent eligibility and notification controls.

The existing operator app already exposes exact bike and dock counts. Public help does not settle all current favourites, alerts or routing capabilities. Audit the current app and observe riders using it before specifying an incremental workflow. The hypothesis is less effort and better decisions at a useful moment, not that a basic availability map is missing.

## What we observed, and what it supports

Across the three August–October 2026 archives there are 2,000,497 source rows. The final cohort contains **1,999,232 eligible completed rentals** with actual local starts in those months. Monthly counts are 645,596, 676,343 and 677,293. The files describe rentals served, not unmet demand, attempted journeys or unique riders. Differences between months are descriptive and may reflect weather, calendar, operations and publication conventions.

Rental mix matters to the proposed experience: 71.4% of eligible rentals are electric-bike records, so “a bike exists” may be too broad for someone who needs a particular type. A member label appears on 71.5%; it does not establish commuting purpose. About 14.5% have no departure station ID and 15.3% no arrival station ID. Almost all missing endpoints occur on electric-bike records, but blank IDs alone do not explain why. Retain these rentals in aggregate activity; restrict only direction-specific station analyses. A dock-based arrival metric also cannot represent every electric-bike return option, since authorised rack returns exist.

Under the assumed weekday windows [07:00,10:00) and [16:00,19:00), Columbus Circle / Union Station has 8,281 known-station departures, ahead of 14th & Irving St NW and Eastern Market Metro. These are candidates for investigation. They are not locations of proven unmet demand. Widening the windows to [06:00,10:00) and [15:00,20:00) retains eight of the top ten, demonstrating that selection depends on the journey-window definition. Monitor the full frozen station cohort to avoid selecting solely on served volume.

The live sample contains two successful snapshots spanning approximately 95 seconds across 875 stations. It proves that source identifiers, metadata, operating flags and report ages can be collected and analysed. Some reports were stale even with successful retrieval. No stable station ranking, weekday recurrence or uncertainty about future weeks is justified from that horizon. Full raw responses stay local; published outputs are aggregate non-commercial analysis under the operator's data terms.

## What I’d need to know before building more

Collect an exploratory two-week pilot to identify coverage problems and validate measurement. Plan 8–12 weeks for recurring weekday questions and block-based uncertainty, extending if data coverage, rare events or atypical conditions warrant it. Before deciding where the feature could help, separate fresh observed zero counts from known closures, stale reports and collector gaps. Check whether acceptable nearby alternatives exist at the relevant times; high volume at a station is insufficient.

If shortages persist across nearby options, prioritise supply and rebalancing with operations. If the information is routinely stale, improve the data path before adding confident notifications. If suitable alternatives exist but riders struggle to find or trust them, the saved-journey workflow becomes more plausible. Rider research must establish tolerance for walking, price, bicycle type and notification timing. No such acceptance evidence is currently claimed.

## How I’d find out whether it helps

Use an operator-linked trial with eligibility defined before allocation and the same neutral departure-intent confirmation in both arms. Persist account allocation and use the **first qualifying intent per account** for the primary ITT outcome: successful rental of an acceptable type within 15 minutes. Include assigned users even if the treatment does not render or they never engage. Reconcile the rental ledger; a missing app event is not proof of no rental, and immature follow-up is not failure. The public dataset cannot measure this outcome.

A hypothetical 70% control success rate, +2 pp practically useful effect, 5% two-sided alpha and 80% power imply 8,079 mature users per arm under independent-user assumptions. This is conditional planning, not a calibrated field sample size. The separate simulation uses only 4,000/arm and finds about 50% power for +2 pp. Its repeated-event null stress test shows 11.35% false positives with naive event independence versus 4.7% with user means. These are synthetic implementation checks, not evidence that the feature works.

Suggested alternatives can shift inventory and affect control users. The proposed initial account contrast estimates own-assignment benefit at the tested saturation; it cannot establish total full-rollout impact. Check geographic/time dependence before confirmatory inference. If that dependence or contamination is material, redesign and repower using network clusters or an operationally credible switchback. Never transfer the user-level sample size to a cluster design.

For a staged expansion, require a valid primary interval excluding zero, a point estimate at least +2 pp, and guardrail precision sufficient to rule out registered harmful increases in failed returns or unnecessary detours. Freshness, safety and tracking integrity are gates. Inconclusive precision calls for more learning, not a success claim. The experiment document defines thresholds, mature cohorts, timing, stopping and secondary measures.

For now, I’d use this work to decide what to learn next: where riders get stuck, whether the information can be trusted, and whether a small change actually helps. I would not use it to claim the feature is ready to launch, that more bikes have become available, or that emissions have fallen.

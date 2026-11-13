# Talking about this project

**A 60-second introduction:** “I wanted to understand whether bike sharing is dependable for a regular journey. The first decision was to separate completed rentals from the opportunities people could not take. I analysed three complete months of published trips to find served patterns, built a collector to measure availability prospectively, and designed a linked intent-to-rental experiment. The present live sample validates collection; it does not tell me where the service is reliably poor. My recommendation is an instrumented saved-journey check with clear uncertainty, and a plan to test its value against the existing app experience.”

## Choices I would defend

- **Why not infer missing bikes from net flows?** We do not observe inventory start state, rebalancing, maintenance or people who gave up. Departures minus arrivals is an activity measure, not a stockout model.
- **Why does missing station information matter?** About one rental in seven has no start station ID. Dropping those trips everywhere would distort the product picture. I keep them in overall volume and explicitly restrict station denominators. Rack returns may explain some missing endpoints, but I cannot assign a cause from blank fields alone.
- **What did validation change?** The website's older description did not match the current CSV. Subminute trips were present. Some October-start rentals ended in an ambiguous November DST hour. I audited exclusions instead of copying assumptions into SQL. Timezone tests also forced UTC-specific assertions because session-local display can hide the correct stored instant.
- **What is the north-star metric?** Not station-time availability. The proposed primary metric is a suitable rental start within 15 minutes of an independently defined departure intent. It is still a departure proxy; return and overall journey quality need guardrails and research.
- **Why first intent?** A user can produce more intents because treatment changes their behaviour. First-intent ITT is simpler to interpret and avoids pretending repeated events are independent. Repeated use remains useful secondary evidence with the right unit of uncertainty.
- **Why not show confidence intervals on every station?** A couple of snapshots are not independent trials, and fixed-period file counts are descriptive. I need many observed days, coverage checks and a dependence-aware target before inferring recurring problems.
- **What can account randomisation miss?** Recommendations shift riders between stations and change inventory for others. A user contrast at half saturation can differ from the effect of everyone using the feature. The account design is a conditional initial proposal, with explicit dependence gates; network/cluster evaluation is needed for rollout claims.
- **Why mention an unsuccessful simulation analysis?** It shows what breaks the result. Differentially missing outcomes produced large bias, while independent-event errors more than doubled false positives in the repeated-user example. Those are lessons from synthetic assumptions, not operator findings.

## How I would handle challenges

“Is Union Station unreliable?” → “It leads served departures in my assumed core weekday windows. That makes it a useful investigation candidate. I have not measured recurrent stockouts there.”

“Can you launch alerts now?” → “The existing app already shows counts. I would first audit the current workflow, learn which decisions riders struggle with, establish fresh-data coverage and validate intent/rental linkage. The proposal tests incremental help, not novelty by assumption.”

“Why not publish a retention cohort?” → “Membership category is not a person ID. Retention needs stable user linkage and an appropriate cohort definition.”

“Would more rides be greener?” → “Not necessarily. I would need to know what mode the ride replaced and include lifecycle effects.”

“Why are you not finished with availability findings?” → “The runnable workflow and initial sample are complete, but observation time cannot be manufactured. Two weeks is exploratory; eight to twelve weeks is a starting point for recurrence and future-week uncertainty, subject to coverage and event counts.”

## Transfer to other products

Delivery marketplaces: completed orders omit abandoned or unserved demand; better ETAs can improve decisions without adding supply. Accommodation: a fresh search response is not proof inventory will remain available at checkout. Consumer notifications: delivery, exposure, engagement and intent have different denominators. Shared marketplaces: a treatment can move scarce supply between users and create spillovers. Across these cases, separate physical supply, information quality, decisions and completed outcomes before selecting metrics or randomisation units.

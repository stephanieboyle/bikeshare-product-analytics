# Experiment proposal: does a timely commute check help a rider start a journey?

**Proposal only. No real operator experiment has been conducted.** Public trips cannot link intent, assignment and rentals. An operator partnership, authenticated app events, rental-ledger linkage and a pre-analysis registration are prerequisites.

## Hypothesis and eligibility

For regular-journey riders who explicitly confirm an imminent departure need, an in-app check of saved stations, report age and suitable nearby alternatives increases successful rental within 15 minutes. It may help navigation without improving underlying supply. We do not test an assumed missing map feature.

Eligibility is evaluated before allocation and before any treatment screen: authenticated adult pilot participants have previously saved an origin/destination pair, chosen acceptable bicycle types and a maximum walking distance, and now actively press a neutral “I intend to leave by bike in the next 15 minutes” confirmation. The common confirmation flow must be identical across arms and available without treatment. Station cohort and pilot geography are fixed beforehand. Exclude employees/test accounts, active rentals, duplicate intents within 30 minutes and users assigned to conflicting trials, using pre-treatment rules. Notification permission is not required for this in-app trial. App opening or viewing availability alone is not an intent event.

The first qualifying event enrols the user. Persist 1:1 allocation by stable operator account ID for the trial, using a versioned server randomisation service. Assignment is logged before exposure and cannot be changed by delivery failures, device changes, later intent or alert engagement. Randomise within preselected origin regions and baseline riding-frequency bands if reliable preperiod linkage exists; use the same strata in analysis. Do not derive eligibility from treatment-induced station selection.

Control: existing map/count experience after the common intent confirmation. Treatment: saved-journey status check, source ages, explicit uncertainty and acceptable nearby options. No inventory reservation or guaranteed destination prediction. Both groups retain standard support and information. Scheduled push alerts are outside this initial estimand: for a later alert trial, eligibility must be established from previously saved schedules independently of an alert-induced app visit.

## Primary estimand, outcome and analysis

Primary estimand: intention-to-treat risk difference in first-intent rental success, treatment minus control, among all randomised eligible users with matured follow-up, under the trial's approximately 50% local treatment saturation. One primary observation per user avoids weighting frequent riders more heavily or conditioning on treatment-induced later intents.

Outcome: at least one operator-confirmed rental start of a previously acceptable bike type within [intent_time, intent_time+15 minutes]. It can occur at any station, including an alternative; assignment to the original origin is not required. Require a valid rental transaction not voided as a test/error according to a pre-specified ledger rule. Timestamp is operator rental start time, not phone upload time. This is a departure-success proxy, not a complete commute measure. It cannot tell whether a rider abandoned cycling for a better mode.

Primary analysis includes assignment even if the check never renders or a notification is not opened. Estimate the unadjusted difference with a two-sided 95% large-sample interval; an adjusted stratum-weighted risk difference is a pre-specified precision analysis. Large samples are required for the normal interval. No alert-openers-only analysis: willingness to open is associated with need, motivation and treatment response, so it breaks randomisation. Exposure and engagement are diagnostic secondary metrics.

Before each data lock, admit intent cohorts by timestamp alone: follow-up must have elapsed plus a 48-hour ledger ingestion/reconciliation allowance, identical by arm. Reconcile complete ledger coverage and late transactions before interpreting absence of rental as zero. Users with unlinked or inaccessible outcomes are unresolved, not automatic failures. Report missingness by arm, worst-case success bounds and sensitivity to plausible missing-outcome differences; do not rely on complete-case analysis under untested missing-at-random assumptions. A material ledger outage delays the analysis. Retain all eligible assignments in cohort accounting.

## Power, duration and stopping

Planning assumptions, not estimates from public trips: control success 70%, minimum useful absolute lift 2 percentage points, α=.05 two-sided, 80% power, equal allocation, one mature observation per account. `planned_n()` uses statsmodels' normal two-proportion method (arcsine effect): **8,079 users per arm**. An independently derived pooled-variance approximation is checked in tests. Allow 10% unresolved linkage in recruitment planning: ceil(8,079/.90)=8,977 per arm; this buffer does not cure biased missingness. Re-estimate feasibility using a blinded instrumentation pilot and confirm the practically useful effect with product/operations costs before registration.

At an assumed 500 newly eligible accounts/day total, 17,954 recruited accounts need about 36 days. Plan six full weeks minimum, then the 15-minute window and 48-hour lag; maximum eight weeks of enrolment. The 500/day rate is hypothetical. If eight weeks cannot produce the target mature sample, conclude insufficient precision rather than extend after viewing effects. Aggregate snapshots and raw trip volumes cannot estimate the eligible-user rate. Do not use this user-level power calculation for a station-cluster or switchback design.

One final primary analysis, no efficacy peeking. Daily safety/instrumentation monitoring uses separate operational thresholds without interpreting early success lift. Pause for consent/privacy breach, unsafe directions, wrong-way or inaccessible route advice, missing assignment, duplicate assignment, or a material ledger failure. Before unblinding outcomes, investigate sample ratio mismatch (diagnostic p<.001), cohort balance, assignment consistency and outcome completeness. Do not discard an inconvenient arm or post-treatment subgroup. Pre-register the harm review and final analysis date.

## Guardrails and decisions

Proposed margins require operator and user confirmation before registration:

| Measure | Proposed decision limit | Measurement dependency |
|---|---|---|
| Failed return / return-support contact within 2h | No increase >0.5 pp; assess upper 95% bound | Rental linkage plus support/return instrumentation; normal rental end alone cannot identify a failed dock attempt |
| Detour judged unnecessary by rider | No increase >1 pp | Randomly sampled follow-up; survey response bias reported |
| Notification opt-outs | No increase >1 pp in a later alert trial | Push delivery and permission tracking; not a guardrail the in-app-only trial can establish |
| Status freshness | ≥95% of treatment status exposures within 300s for both feed/report ages | Client payload ages; never just HTTP age |
| Safety/accessibility | Any serious attributable route incident triggers review | Research and support; low frequency cannot establish safety statistically |

Guardrails are conjunctive gates, not a collection of opportunities to find a positive result. Limit the primary claim to one outcome; secondary outcomes are descriptive with intervals and no independent launch claims. If formal secondary claims are needed, register a hierarchical order or multiplicity correction.

Expand a staged rollout only if the primary 95% lower bound exceeds zero, the point estimate is at least +2 pp, instrumentation is valid and guardrail upper bounds rule out the registered harm margins. This rule is stricter than significance alone; 80% power for zero-effect rejection does not imply 80% probability of passing all launch criteria. If an interval includes both no benefit and useful benefit, iterate or run a separately registered follow-up. Stop the tested version if the upper bound is below +2 pp or material harm is found. A significant but clearly sub-useful lift does not justify expansion. Wide guardrail intervals mean uncertainty, not proof of no harm.

## Secondary learning

Time to rental: use a pre-specified 15-minute restricted mean time measure, assigning the full 15 minutes to non-renters, rather than comparing times among successful renters only. Alternative accepted: event-measurable but engagement, not success. Suitable alternative found and usefulness require feedback; nonresponse is reported. Return difficulty needs new failed-dock/support instrumentation and research. Walking/detours require voluntary bounded location or self-report; do not infer distance walked from station coordinates. Repeated eligible intents are secondary and need account-clustered uncertainty, not independent-event errors.

## Interference and choice of design

Alternative suggestions move demand. Treated users can consume bikes or docks that control riders need. Station networks interact, so an account trial is not a clean estimate of system-wide policy impact. The chosen initial design is defensible for the narrower question of a direct assignment benefit at the tested treatment saturation. With independent allocation of other accounts, it targets the average own-assignment contrast over that random allocation distribution. Inventory feedback can also correlate users' outcomes: simple binomial uncertainty is a planning approximation, not guaranteed in the field. Before a confirmatory claim, use a multiweek pilot to assess origin/day dependence and a pre-specified joint geographic/day dependence sensitivity. If dependence materially changes precision or assignment exposure is concentrated in a few interacting neighbourhoods, the account trial remains feasibility evidence; redesign and repower rather than claim confirmatory confidence from the user calculation.

| Design | What it helps estimate | Main trade-offs |
|---|---|---|
| Persistent account randomisation (chosen first) | Own assignment effect at approximately 50% saturation | Good balance and many units; spillovers contaminate the contrast and may correlate outcomes; cannot establish full-rollout lift |
| Geographic network clusters | Total within-area policy effect if cross-boundary flows small | Nearby stations must be grouped using preperiod flows; buffer/contamination rules fixed; likely few effective clusters, unequal size and baseline imbalance. Needs cluster-level power with ICC and network flows, not account n |
| Cluster switchback by time | Policy effect within places across assigned periods | More repeated periods but fewer independent units; inventory displacement persists into next period. Need justified washout, blocked weekday/time randomisation, period-level inference, weather/time-trend adjustment; notification learning and saved preferences can carry over |

A full-rollout claim requires a later cluster/saturation trial after mapping station interactions and collecting cluster/time variance. No credible cluster count, ICC or washout duration can be derived from the current pilot, so no fabricated cluster sample-size number is supplied. The simulation's simple spillover scenario illustrates the estimand gap; it does not solve network interference or validate field precision.

# Synthetic experiment validation

**Every result in `reports/simulation.json` and figure 05 is simulated. No operator experiment took place.** Fixed seed 20261113, 2,000 repetitions per scenario, 4,000 accounts per arm. Parameters are illustrative and are not fitted to public trips. This sample is intentionally below the 8,079/arm planning size so that power is not assumed to be high.

## Data-generating process

First-intent scenarios use independent Bernoulli rental outcomes with control p=.70 and treatment p=.70 (null) or .72 (plausible absolute +.02 effect). Binomial counts generate exactly the sufficient statistics. The estimator is the difference in arm proportions with a two-sided 95% normal/Wald interval. Large synthetic samples justify this demonstration; it is not proposed for tiny or extreme-rate cells. Tests compare both an independently calculated variance example and statsmodels' `confint_proportions_2indep(method='wald')`. Power is checked against a first-order normal formula and calculated with statsmodels.

Missing-at-random scenario independently observes 90% of success and failure outcomes in each arm, then demonstrates complete-case inference under that explicit assumption. The differential-missing scenario observes control outcomes with .90 probability, but treatment successes with .95 and failures with .70; complete-case inference is deliberately invalid for the full ITT target. Real ledger linkage must not be assumed missing at random merely because the simple scenario behaves well.

Immature follow-up: only 75% of enrolled outcomes have matured, independently of allocation/outcome. The deliberately flawed analysis counts all immature outcomes as failure, attenuating a true 2 pp lift towards 1.5 pp. The mature-cohort scenario limits the estimand to entrants whose fixed enrolment-time windows have matured. It preserves effect under this DGP but has less information. This does not endorse dropping missing outcomes after follow-up; maturity is a time rule defined before outcome inspection.

Simple spillover: `P(success)=.70+.02*own_assignment+.02*local_saturation`. At saturation .5 the arms have .71/.73 success and the direct contrast is .02, while all-treated versus all-control would be .74−.70=.04. Simulation diagnoses the direct contrast; it cannot establish the rollout effect. Saturation is fixed and common, so this simplified scenario does not create realistic correlated inventory feedback, spatial spillover or depletion. It illustrates an estimand difference, not a validated network model.

Repeated-event stress test under the null: each user has four intents with a latent propensity drawn from Beta(2.8,1.2), mean .70 and intraclass correlation .20. Both arms have the same DGP. Treating all events independently understates uncertainty. A user-mean difference with variance across user means accommodates dependence within accounts in this balanced four-event case. It is not a general proof for unequal, treatment-induced intent counts or interference across accounts.

## Diagnostics and interpretation

For each scenario record mean estimate, bias, 95% interval coverage, zero-effect rejection rate and Monte Carlo standard errors. Under a null, rejection is false positives; under +2 pp, rejection is power. Bias MC SE is the sample SD of estimates divided by √repetitions; rate MC SE is √[r(1−r)/repetitions]. For zero observed misses or rejections, that plug-in SE is zero but uncertainty is not: the approximate rule-of-three upper rate is 3/2000=.15%. Do not call a boundary rate exact.

Current reproducible results:

| Scenario | Bias (pp) | Coverage | Rejection of zero |
|---|---:|---:|---:|
| Null | +0.034 | 95.2% | 4.8% false positives |
| Plausible +2 pp | −0.009 | 94.35% | 49.85% power |
| Missing at random | +0.044 | 94.95% | 47.3% power |
| Differential missing, invalid analysis | +5.718 | 0/2000 cover | 2000/2000 reject |
| Immature coded as failure, invalid | −0.504 | 93.35% | 26.9% power |
| Mature cohort | −0.005 | 95.25% | 39.85% power |
| Simplified spillover, direct target | −0.011 | 94.5% | 50.05% power |
| Naive independent repeat events, null | −0.012 | 88.65% | 11.35% false positives |
| User-mean repeat events, null | −0.012 | 95.3% | 4.7% false positives |

Null false-positive MC SE is about 0.48 percentage points, so 4.8% is compatible with 5%. The +2 pp power MC SE is about 1.12 pp. Coverage in one scenario need not equal exactly 95%; interpret repeated-simulation variability and systematic biases together. No seed or parameter was selected to produce a favourable result.

The proposed primary field trial also uses first eligible intent per account, but local inventory dependence, stratification, ledger reconciliation and unknown eligible-user rates remain unvalidated here. The repeated-user diagnostic and simplified spillover are stress demonstrations; neither makes this calculation adequate for geographic cluster randomisation or a switchback. Field design feasibility gates in `experiment_design.md` must be satisfied before a confirmatory trial.

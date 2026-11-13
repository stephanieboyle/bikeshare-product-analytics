import numpy as np
import pytest
from scipy.stats import norm
from statsmodels.stats.proportion import confint_proportions_2indep

from bikeshare_analytics.simulation import difference_interval, planned_n


def test_interval_against_reference_and_independent_case():
    estimate, low, high = difference_interval(60, 100, 50, 100)
    assert estimate == pytest.approx(.1)
    half = norm.ppf(.975) * np.sqrt(.6 * .4 / 100 + .5 * .5 / 100)
    assert (low, high) == pytest.approx((.1 - half, .1 + half))
    reference = confint_proportions_2indep(60, 100, 50, 100, method='wald')
    assert (low, high) == pytest.approx(reference)


def test_symmetry_and_null():
    a, low, high = difference_interval(50, 100, 50, 100)
    assert a == 0 and low == pytest.approx(-high)
    b, blow, bhigh = difference_interval(50, 100, 60, 100)
    original = difference_interval(60, 100, 50, 100)
    assert (b, blow, bhigh) == pytest.approx(tuple(-x for x in (original[0], original[2], original[1])))


def test_power_matches_normal_approximation_scale():
    # Independent first-order formula, p=.71 pooled: 2*p*(1-p)*(zalpha+zpower)^2/delta^2.
    approximate = 2 * .71 * .29 * (norm.ppf(.975) + norm.ppf(.8)) ** 2 / .02 ** 2
    assert abs(planned_n() / approximate - 1) < .02
    assert planned_n(effect=.01) > 3.8 * planned_n()


def test_invalid_counts():
    with pytest.raises(ValueError):
        difference_interval(101, 100, 50, 100)

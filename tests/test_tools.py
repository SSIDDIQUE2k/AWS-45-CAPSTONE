from agent.tools import amortization_schedule, apr_to_apy, debt_to_income_ratio


def test_apr_to_apy_monotonic():
    apr = 0.1
    apy = apr_to_apy(apr)
    assert apy > apr


def test_dti_basic():
    assert debt_to_income_ratio(1500, 6000) == 0.25


def test_amortization_total_paid():
    res = amortization_schedule(100000, 0.05/12*12, 30)
    assert 'monthly_payment' in res
    assert res['total_paid'] > 100000


from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AmortizationPayment:
    month: int
    principal: float
    interest: float
    balance: float


def amortization_schedule(principal: float, annual_rate: float, years: int) -> Dict:
    r = annual_rate / 12.0
    n = years * 12
    if r == 0:
        payment = principal / n
    else:
        payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    schedule: List[AmortizationPayment] = []
    balance = principal
    total_interest = 0.0
    for i in range(1, n + 1):
        interest = balance * r
        principal_paid = payment - interest
        balance = max(0.0, balance - principal_paid)
        total_interest += interest
        schedule.append(AmortizationPayment(i, round(principal_paid, 2), round(interest, 2), round(balance, 2)))
    return {
        'monthly_payment': round(payment, 2),
        'total_interest': round(total_interest, 2),
        'total_paid': round(total_interest + principal, 2),
        'schedule': [p.__dict__ for p in schedule],
    }


def apr_to_apy(apr: float, periods_per_year: int = 12) -> float:
    return (1 + apr / periods_per_year) ** periods_per_year - 1


def debt_to_income_ratio(total_monthly_debt: float, gross_monthly_income: float) -> float:
    if gross_monthly_income <= 0:
        return 0.0
    return total_monthly_debt / gross_monthly_income


"""
Sample client profiles for the HAI Portfolio App.
Each client represents a different test scenario.
"""

SAMPLE_CLIENTS = {
    # Case A: Normal — mid-horizon growth investor, no conflicts
    "Client A — Growth Investor": {
        "client_id": "C1001",
        "name": "Client A",
        "age": 29,
        "horizon_years": 12,
        "liquidity_need": "medium",
        "goal": "long_term_growth",
        "risk_score_100": 68,
        "current_weights": {
            "Equity": 0.55, "Bond": 0.30, "Gold": 0.05, "Cash": 0.10
        },
    },
    # Case B: Boundary — short horizon but high risk score
    "Client B — Short Horizon, High Score": {
        "client_id": "C1002",
        "name": "Client B",
        "age": 45,
        "horizon_years": 1,
        "liquidity_need": "high",
        "goal": "home_purchase",
        "risk_score_100": 78,
        "current_weights": {
            "Equity": 0.60, "Bond": 0.20, "Gold": 0.10, "Cash": 0.10
        },
    },
    # Case C: Conflict — capital preservation goal but aggressive preference
    "Client C — Goal vs Preference Conflict": {
        "client_id": "C1003",
        "name": "Client C",
        "age": 52,
        "horizon_years": 5,
        "liquidity_need": "low",
        "goal": "capital_preservation",
        "risk_score_100": 82,
        "current_weights": {
            "Equity": 0.70, "Bond": 0.15, "Gold": 0.05, "Cash": 0.10
        },
    },
    # Case D: Conservative retiree — everything aligned, low risk
    "Client D — Conservative Retiree": {
        "client_id": "C1004",
        "name": "Client D",
        "age": 67,
        "horizon_years": 20,
        "liquidity_need": "medium",
        "goal": "retirement_income",
        "risk_score_100": 32,
        "current_weights": {
            "Equity": 0.25, "Bond": 0.50, "Gold": 0.10, "Cash": 0.15
        },
    },
}

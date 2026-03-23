"""
logic.py — Core decision logic for the HAI Portfolio App.

This module contains:
  1. Suitability rules (pre-filter before allocation)
  2. Risk bucket mapping (score -> bucket)
  3. Base allocation templates (bucket -> weights)
  4. Suitability cap enforcement (cap equity based on constraints)
  5. Review flag detection (conflicting inputs -> escalation)
  6. Explanation generation (state -> human-readable rationale)
  7. Uncertainty classification

All functions are pure: they take data in, return data out, no side effects.
This makes them easy to test, audit, and reuse across UI / memo / log.
"""


# ── 1. Suitability rules ────────────────────────────────────
def suitability_rules(client: dict) -> dict:
    """
    Determine constraints BEFORE allocation.
    Returns a dict of caps and restrictions.
    """
    equity_cap = 0.90
    cash_floor = 0.00
    restricted = []

    # Short horizon -> hard cap on equity
    if client["horizon_years"] <= 2:
        equity_cap = min(equity_cap, 0.30)
        cash_floor = max(cash_floor, 0.15)

    # High liquidity need -> cap equity, raise cash floor
    if client["liquidity_need"] == "high":
        equity_cap = min(equity_cap, 0.40)
        cash_floor = max(cash_floor, 0.10)

    # Capital preservation goal -> tighter equity cap
    if client["goal"] == "capital_preservation":
        equity_cap = min(equity_cap, 0.35)

    # Retirement income -> moderate cap
    if client["goal"] == "retirement_income":
        equity_cap = min(equity_cap, 0.50)

    return {
        "equity_cap": equity_cap,
        "cash_floor": cash_floor,
        "restricted": restricted,
    }


# ── 2. Risk bucket ──────────────────────────────────────────
def risk_bucket(score: float) -> str:
    """Map a 0-100 risk score to a named bucket."""
    if score < 25:
        return "Very Conservative"
    elif score < 45:
        return "Conservative"
    elif score < 60:
        return "Balanced"
    elif score < 75:
        return "Growth"
    else:
        return "Aggressive"


# ── 3. Base allocation templates ─────────────────────────────
ALLOCATION_TEMPLATES = {
    "Very Conservative": {"Equity": 0.15, "Bond": 0.60, "Gold": 0.10, "Cash": 0.15},
    "Conservative":      {"Equity": 0.30, "Bond": 0.50, "Gold": 0.10, "Cash": 0.10},
    "Balanced":          {"Equity": 0.50, "Bond": 0.35, "Gold": 0.10, "Cash": 0.05},
    "Growth":            {"Equity": 0.70, "Bond": 0.20, "Gold": 0.05, "Cash": 0.05},
    "Aggressive":        {"Equity": 0.85, "Bond": 0.10, "Gold": 0.05, "Cash": 0.00},
}


def base_allocation(bucket: str) -> dict:
    """Return the template allocation for a given risk bucket."""
    return ALLOCATION_TEMPLATES[bucket].copy()


# ── 4. Apply suitability caps ────────────────────────────────
def apply_caps(weights: dict, equity_cap: float, cash_floor: float = 0.0) -> dict:
    """
    Enforce suitability constraints on raw allocation weights.
    If equity exceeds cap, redistribute excess to bond (70%) and cash (30%).
    If cash is below floor, pull from other assets proportionally.
    """
    w = weights.copy()

    # Enforce equity cap
    if w["Equity"] > equity_cap:
        excess = w["Equity"] - equity_cap
        w["Equity"] = equity_cap
        w["Bond"] += excess * 0.7
        w["Cash"] += excess * 0.3

    # Enforce cash floor
    if w["Cash"] < cash_floor:
        deficit = cash_floor - w["Cash"]
        w["Cash"] = cash_floor
        # Pull proportionally from equity and bond
        eq_bond = w["Equity"] + w["Bond"]
        if eq_bond > 0:
            w["Equity"] -= deficit * (w["Equity"] / eq_bond)
            w["Bond"] -= deficit * (w["Bond"] / eq_bond)

    # Normalize to sum to 1
    total = sum(w.values())
    return {k: round(v / total, 4) for k, v in w.items()}


# ── 5. Review flags ─────────────────────────────────────────
def review_flags(client: dict, weights: dict) -> list:
    """
    Detect conditions that should trigger human review.
    Returns a list of plain-English flag descriptions.
    """
    flags = []

    # Short horizon but still high equity after caps
    if client["horizon_years"] <= 2 and weights["Equity"] > 0.30:
        flags.append(
            "Short horizon with high equity recommendation"
        )

    # High liquidity need but low cash
    if client["liquidity_need"] == "high" and weights["Cash"] < 0.15:
        flags.append(
            "High liquidity need but cash allocation may be insufficient"
        )

    # Aggressive score conflicts with conservative goal
    if client["risk_score_100"] >= 75 and client["goal"] == "capital_preservation":
        flags.append(
            "Aggressive risk score conflicts with capital preservation goal"
        )

    # Very low experience / young with aggressive allocation
    if client["age"] < 25 and weights["Equity"] > 0.70:
        flags.append(
            "Very young investor with high equity exposure — confirm experience"
        )

    # Current holdings very different from recommendation
    current = client.get("current_weights", {})
    if current:
        eq_diff = abs(current.get("Equity", 0) - weights["Equity"])
        if eq_diff > 0.25:
            flags.append(
                f"Equity shift of {eq_diff:.0%} from current holdings — "
                "large rebalancing required"
            )

    return flags


# ── 6. Uncertainty level ─────────────────────────────────────
def uncertainty_level(client: dict, flags: list) -> str:
    """Classify output uncertainty as low / medium / high."""
    if len(flags) >= 2:
        return "high"
    if len(flags) == 1:
        return "medium"
    if client["horizon_years"] <= 3:
        return "medium"
    return "low"


# ── 7. Explanation generator ─────────────────────────────────
def build_explanation(client: dict, bucket: str, suit: dict,
                      weights: dict, flags: list) -> str:
    """
    Produce a human-readable explanation of the recommendation.
    This is used by the assistant panel and the memo.
    """
    w = weights
    lines = [
        f"Your risk score is {client['risk_score_100']}/100, "
        f"placing you in the **{bucket}** bucket.",
        "",
        f"- Investment horizon: {client['horizon_years']} years",
        f"- Liquidity need: {client['liquidity_need']}",
        f"- Goal: {client['goal'].replace('_', ' ')}",
        "",
        f"Suitability constraints applied:",
        f"- Equity cap: {suit['equity_cap']:.0%}",
        f"- Cash floor: {suit['cash_floor']:.0%}",
        "",
        f"**Recommended allocation:**",
        f"- Equity: {w['Equity']:.0%}",
        f"- Bond: {w['Bond']:.0%}",
        f"- Gold: {w['Gold']:.0%}",
        f"- Cash: {w['Cash']:.0%}",
    ]

    if flags:
        lines.append("")
        lines.append("⚠️ **Review flags:**")
        for f in flags:
            lines.append(f"- {f}")

    return "\n".join(lines)


# ── 8. Risk description ─────────────────────────────────────
def build_risk_description(client: dict, weights: dict,
                           flags: list, unc: str) -> str:
    """Describe the main risks for the assistant panel."""
    lines = [
        f"**Uncertainty level: {unc.upper()}**",
        "",
        "Key risks for this recommendation:",
        "",
        "1. **Market drawdown** — equity allocation of "
        f"{weights['Equity']:.0%} means the portfolio could "
        "decline significantly in a downturn.",
        "",
        "2. **Risk tolerance mismatch** — the stated risk score "
        f"({client['risk_score_100']}) may not reflect actual "
        "behavior during market stress.",
        "",
        "3. **Assumption risk** — expected returns and correlations "
        "are based on historical data and may not hold in future regimes.",
    ]

    if client["horizon_years"] <= 3:
        lines.append("")
        lines.append(
            "4. **Short horizon risk** — with only "
            f"{client['horizon_years']} year(s), there is limited "
            "time to recover from adverse market movements."
        )

    if flags:
        lines.append("")
        lines.append("Additional concerns flagged by the system:")
        for f in flags:
            lines.append(f"- {f}")

    return "\n".join(lines)


# ── 9. Pipeline: run everything ──────────────────────────────
def run_pipeline(client: dict) -> dict:
    """
    Execute the full recommendation pipeline for a client.
    Returns a dict with all computed state.
    """
    bucket = risk_bucket(client["risk_score_100"])
    suit = suitability_rules(client)
    raw_weights = base_allocation(bucket)
    weights = apply_caps(raw_weights, suit["equity_cap"], suit["cash_floor"])
    flags = review_flags(client, weights)
    unc = uncertainty_level(client, flags)
    explanation = build_explanation(client, bucket, suit, weights, flags)
    risk_desc = build_risk_description(client, weights, flags, unc)

    return {
        "bucket": bucket,
        "suit": suit,
        "raw_weights": raw_weights,
        "weights": weights,
        "flags": flags,
        "uncertainty": unc,
        "explanation": explanation,
        "risk_description": risk_desc,
        "review_required": len(flags) > 0,
    }

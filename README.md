# Week 10: HAI Portfolio Dashboard

A governed prototype demonstrating Human-AI Interaction in financial products.

## Quick Start

```bash
# 1. Install dependencies
pip install streamlit pandas plotly

# 2. Run the app
cd app
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Passwords

| Role     | Password   | Can do                                    |
|----------|------------|-------------------------------------------|
| User     | `demo`     | View dashboard, ask assistant, export memo |
| Reviewer | `reviewer` | All above + override + view full logs      |

Passwords are in `.streamlit/secrets.toml` (not committed to git in real projects).

## Project Structure

```
app/
├── app.py              # Streamlit main — tabs, UI, interactions
├── logic.py            # Core logic — suitability, allocation, flags
├── memo.py             # Memo generation (markdown)
├── auth.py             # Password gate + role-based permissions
├── utils.py            # Audit logging, formatting helpers
├── sample_data.py      # 4 sample client profiles (A/B/C/D)
├── .streamlit/
│   └── secrets.toml    # Passwords (demo only)
└── logs/
    └── audit.jsonl     # Append-only audit log (auto-created)
```

## Architecture

```
Input Layer    →  sample_data.py (client profile)
                      ↓
Logic Layer    →  logic.py (suitability → bucket → allocation → flags)
                      ↓
HAI Layer      →  disclosure, confidence note, review trigger, override
                      ↓
Output Layer   →  dashboard | assistant | memo export | audit log
```

## The Four Panels

### 1. Dashboard
- Risk score, bucket, horizon, uncertainty level
- Pie chart (recommended allocation)
- Grouped bar chart (current vs recommended)
- Warning box (review flags)
- Disclosure box (always visible)

### 2. Assistant
- Answers 4 fixed question types from rule-based logic
- Responses change dynamically based on selected client
- Not free-form LLM — fully traceable to score + rules

### 3. Memo Export
- Full markdown memo with profile, allocation, rationale, disclosure
- Download as .md or .txt
- Option to record export in audit log

### 4. Review Log
- Override form (reviewer role only)
- Requires reason + adjusted weights
- All actions logged to `logs/audit.jsonl`
- Filter log by event type

## Sample Clients

| Client | Scenario | Expected Behavior |
|--------|----------|-------------------|
| A — Growth Investor | Normal case | Growth bucket, no flags |
| B — Short Horizon | Boundary case | Suitability caps equity to 30%, flags triggered |
| C — Goal Conflict | Conflict case | Score=82 but goal=preservation, flags triggered |
| D — Conservative Retiree | Low risk | Conservative bucket, no flags |

## HAI Checklist

### A. Usability
- [x] Recommendation clearly visible (pie chart + metrics)
- [x] Rationale understandable (assistant panel)
- [x] Next action clear (review status shown)
- [x] Uncertainty visible (uncertainty level in dashboard)
- [x] Interface not overconfident (disclosure always shown)

### B. Risk Control
- [x] Scope and limitations disclosed
- [x] Review triggered for risky cases
- [x] Outputs can be overridden (reviewer role)
- [x] Overrides recorded with reason + timestamp
- [x] Secrets handled safely (secrets.toml, not hardcoded)
- [x] Basic access control (user vs reviewer roles)

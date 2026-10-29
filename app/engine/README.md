# ShareSafe Decision & Fairness Engine (P3)

This package contains the pure, deterministic decision and fairness engine for ShareSafe.

## Core Properties
1. **Explainable & Deterministic**: Pure functions with zero database access, zero network calls, and zero LLM dependencies. Identical inputs always produce identical decisions and priority scores.
2. **Untrusted Free-Text Guard**: `RequestCtx.justification` is untrusted free text and is **never** read by the engine (prompt injection resilient).
3. **Transparent Priority Scoring**: Transparent priority calculation with documented weights in `app/engine/fairness.py` (`FAIRNESS_CONFIG`).
4. **Advisory Decisions**: The engine produces recommendations (`recommend_approve`, `recommend_reject`, `waitlist`, `needs_human`). Final authority remains with the equipment owner.

---

## 5-Line Usage Example for Lead (P1)

```python
from datetime import datetime, timezone
from app.engine.decision import evaluate_request

# Evaluate borrower request against resource constraints and historical usage
decision = evaluate_request(
    request=request_ctx,      # RequestCtx (start, end, user, etc.)
    resource=resource_ctx,    # ResourceCtx (rules dict, readiness)
    user=user_ctx,            # UserCtx (year, training certifications)
    history=existing_bookings,# List[BookingCtx]
    competing=competing_reqs, # List[RequestCtx] for overlapping slot (if any)
    now=datetime.now(timezone.utc),
)

# Decision contains verdict, list of RuleResults, priority breakdown, and plain-language explanation
print(decision.verdict)       # Verdict.RECOMMEND_APPROVE / RECOMMEND_REJECT / WAITLIST / NEEDS_HUMAN
print(decision.explanation)   # Deterministic plain-language explanation
```

---

## Anti-Monopolisation & Proxy Detection

```python
from app.engine.fairness import detect_proxy_patterns

# Flags coordinated back-to-back bookings by teammates and repetitive hoarding
flags = detect_proxy_patterns(all_bookings)
for flag in flags:
    print(flag.kind, flag.user_ids, flag.reason)
```

---

## Resource Rules Schema (`app/engine/schema.py`)
Stored in `resources.rules` JSON:
```json
{
  "min_year": 3,
  "required_training": ["gpu_safety"],
  "max_hours_per_booking": 4,
  "min_notice_hours": 2,
  "weekend_requires_supervisor": true,
  "max_consecutive_bookings": 2,
  "recent_usage_cap_hours_30d": 20,
  "requires_inspection_within_days": 30
}
```
All fields optional. Validated using `ResourceRules` Pydantic model.

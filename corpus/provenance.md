# Corpus provenance

All documents below are self-authored/synthetic for this project. No real
clinic, patient, or payer data is used, per PLAN.md section 3's hard
constraint.

| File | Description | Purpose |
|---|---|---|
| `prep_current.txt` | Current pre-procedure prep sheet (bloodwork) | Ground truth: 8 hour fast |
| `prep_stale.txt` | An outdated version of the same prep sheet, still reachable in the index | Planted contradiction (PLAN.md section 8): says 12 hours |
| `intake_faq.txt` | General intake FAQ: arrival time, documents, coverage | Ground truth for non-fasting claims |

# 0.4 acceptance evidence - 13 October 2026

Scope: a local support handbook with public synthetic documents. The application searches, shows source text, prepares editable tickets and optionally selects sentences with a local model. This release is suitable for local portfolio review; organizational rollout requires the controls described in OPERATIONS.md.

- 44 Python unit/API tests passed locally and in GitHub Actions.
- Unchanged benchmark: 22/24 correct source or abstention; Recall@3 16/18; six unanswerable cases abstain; two paraphrase failures remain.
- Chromium acceptance checks passed: 12 guides, expected printer source, preserving edited tickets, rejecting late drafts, busy feedback, changed question, unsupported-query escalation, 390px layout without horizontal overflow and no uncaught browser errors. Browser model responses were controlled mocks.
- Actual Windows CPU model startup, POST /api/draft and stop-file shutdown passed. Inference 2.34 seconds, 235 input + 44 output tokens. Both ports released. One synthetic model case is not broad quality validation. Interactive Ctrl+C was not separately exercised.
- Desktop and mobile screenshots visually reviewed: legible Persian text, consistent spacing, no overlap or clipping observed in these states.

Verified CI: https://github.com/saintedwind/persian-it-evidence/actions/runs/38372693421
Tested commit: 36361b5c1ddebda74b3eaa86748d078290b69503
See browser-v04.json, lifecycle-v04.json, handbook-desktop.png and handbook-mobile.png.

The prior launcher-cleanup failure is historical and remains recorded in the v0.3 report. The new stop-file path passed end to end. No paid inference API, real customer data, adoption, productivity savings or production security claim.

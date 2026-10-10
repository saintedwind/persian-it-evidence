# From a support question to a traceable ticket

Independent prototype by Peyman Gholamhosseini, October 2026. No customer deployment or business savings are claimed.

## The workflow

A colleague reports that the printer queue has stopped. Searching scattered procedures can be slower than describing the problem itself. This handbook keeps the source visible, lets the reader copy a referenced procedure, and prepares an editable ticket if the problem remains unresolved. The ticket is not sent anywhere.

The test corpus contains 12 public synthetic IT guides and one restricted fixture. These are demonstration materials, not approved instructions for a real organization.

## Implementation and decisions

1. A Python service normalizes Persian text and ranks public documents with BM25. Authorization filtering precedes ranking; a browser cannot request a staff role.
2. The interface shows the actual source and document identifier. The reader remains responsible for deciding whether a procedure applies.
3. An optional local Qwen3-0.6B model selects numbered sentences from one retrieved document. The application validates the identifiers and displays original sentences in source order. It rejects invalid or truncated selections.
4. Search does not invoke the model. Explicit draft requests use a 96-output-token budget and no automatic retry. Unsupported retrieval skips inference entirely.

Initial free-form Persian responses were unreliable. The narrower sentence-selection design retains traceability but can omit necessary steps or choose irrelevant text. The full source must remain visible; this is not an autonomous troubleshooting system.

## Evidence

The unchanged 24-question author-written benchmark returns the correct source or abstains on 22 cases. Recall@3 is 16/18; all six unanswerable cases abstain. Two indirect Persian paraphrases still fail. The dataset is small and is not an independent test of production quality.

The regression gate preserves all 22 previously successful cases individually, including abstentions, and blocks restricted-document retrieval. Known failures may improve without changing the gate. The 39-test suite also exercises input validation, public routes, invalid model output, concurrency limits and failure handling. Model calls in unit tests are mocked; actual local inference evidence is recorded separately in `local-model-smoke.json` and `local-model-http.json`.

## What would make this a real pilot

The next evidence needed is feedback from willing testers and a permissioned, owner-reviewed document set. Before any organizational rollout: implement authentication, document approval/revision handling, a separately reviewed evaluation set and an agreed ticket destination. Do not use this prototype for credential resets or other consequential actions automatically.

See [operator notes](OPERATIONS.md), [failure analysis](FAILURE_ANALYSIS.md), and [local model limitations](LOCAL_MODEL.md).

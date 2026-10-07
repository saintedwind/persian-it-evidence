# Portfolio delivery gates

Dates are planning targets, not claims of completed work. The owner learns and verifies each release with AI assistance.

## v0.1 — complete locally

- [x] Persian lexical retrieval, source excerpts, abstention heuristic.
- [x] Public-scope local API and Persian browser UI.
- [x] 18 local tests, 24-question evaluation, retained failure cases.
- [x] Documentation, screenshot, and CI configuration.
- [x] Publish repository and observe GitHub Actions actually passing (7 October 2026).
- [ ] Owner independently runs the demo, explains BM25 vs embeddings, and fixes a small retrieval issue.

## v0.2 — next 7–14 working days

- [ ] Select and verify a multilingual embedding model and license; record exact revision.
- [ ] Use real, permissioned public IT documentation with provenance and redistribution checks.
- [ ] Add ingestion/chunking with stable document and chunk IDs.
- [ ] Compare BM25, dense search, and reciprocal-rank fusion on a frozen evaluation set.
- [ ] Evaluate at least 60 questions, with separate tuning and evaluation splits.
- [ ] Report Recall@k, MRR, retrieval latency, storage, model size, and all regressions.

## v0.3 — weeks 3–4

- [ ] Add a chosen local or API LLM only after cost/access choices are explicit.
- [ ] Validate source IDs, evaluate groundedness and refusal separately from retrieval.
- [ ] Build a production framework API, proper authentication, logging redaction, and rate limits.
- [ ] Exercise prompt-injection and document-access tests; record residual risks.
- [ ] Build and test the container; publish a short walkthrough and measured release notes.

## Second flagship — weeks 5–8: Vision Quality Lab

Modernize the owner's earlier computer-vision work into an evaluation-driven video pipeline. Start with a public, licensed non-sensitive visual-inspection dataset. Compare a simple baseline and a modern detector; split by source/video to reduce leakage; report precision/recall, errors, CPU latency, and model size. Add reproducible training/inference, a small API, and a demo. Use synthetic or properly licensed video; do not claim validated driver-safety or medical performance from a demo.

## Third flagship — weeks 9–12: Forecast Reliability Lab

Build on earlier air-pollution forecasting work. Use dated public environmental data with provenance. Compare a naive seasonal forecast, a statistical/ML baseline, and the proposed neural model. Use rolling time splits, leakage checks, missing-data handling, uncertainty intervals, and drift reporting. A measured simple model is preferable to an unsupported LSTM superiority claim.

## Weekly cadence

Spend roughly 60% of available project time building, 25% testing/evaluating, and 15% documenting and explaining in English/Persian. Every week ship one reviewable change, one failure analysis, and a three-minute walkthrough. Review daily job findings, but change the core project direction only after a repeated pattern across independent employers.

## Publish rule

Describe completed behavior, dataset limitations, AI assistance, and observed metrics. Do not list unbuilt roadmap features as skills demonstrated by this repository. Do not describe a portfolio release as paid employment or production adoption.

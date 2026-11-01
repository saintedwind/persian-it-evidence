# Answer routing v0.7 — actual behavior and failures

## Implemented

The demo exposes three modes: internal-only, model-only, and hybrid (default). Submit a question once; after retrieval the model response is requested automatically. The retry button remains explicit. Model-only answers do not use retrieved text and the internal result panel is hidden. Hybrid tries source-grounded synthesis first, then switches to uncited general model knowledge on insufficient evidence or context limitation. Unavailable, invalid or truncated model outputs are not silently treated as evidence failure and replaced.

Every response carries `answer_source`: `internal`, `model`, or `none`, and `requested_mode`. Internal answers retain their source and checked quote. General-model answers carry **no internal citations** and are explicitly labeled unverified model knowledge; no externally verified source is claimed. This version is sequential fallback, not a blended multi-source answer.

The model has no live internet. An explicit freshness heuristic plus model self-report requires a live source for recognized current questions. Such responses return `needs_live_source` without displaying a potentially stale assertion. This guard is narrow and can miss other wording. Private credential value requests are refused in every mode by the existing narrow request guard; this is not general authorization or safety classification.

## Real HTTP/model tests

Raw initial evidence: [routing-live-v07.json](routing-live-v07.json). Cases were declared before inference. Model: official Qwen3-1.7B Q8_0 on CPU, same verified weights/runtime as the prior release. No mocks, API credentials, or paid inference were used.

| Initial case | API status | Answer source | Seconds |
|---|---|---|---:|
| internal-supported | answer_ready | internal | 17.977 |
| general-geography | answer_ready | model | 9.488 |
| general-science | answer_ready | model | 15.324 |
| strict-no-fallback | insufficient_evidence | none | 0.049 |
| model-only | answer_ready | model | 9.878 |
| current-python | needs_live_source | none | 2.634 |
| current-president | answer_ready | model | 2.543 |
| private | refused | none | 0.002 |

### Quality findings, including unsuccessful cases

- Ransomware: source-based definition and checked quote were consistent with the displayed document.
- Capital of Japan: general fallback produced a false capital and invented location details. Correct answer is Tokyo; checked against [Japan's Ministry of Foreign Affairs](https://www.mofa.go.jp/policy/economy/summit/2008/venue/tokyo_01.html).
- Blue sky: general fallback generated repetitive and scientifically incorrect text. Compare the [NASA explanation](https://spaceplace.nasa.gov/blue-sky/en/) of atmospheric scattering. This is a factual failure despite valid JSON and a correct model-origin label.
- DNS in model-only mode: captured the name-to-IP concept but with imprecise language; no internal evidence citation was supplied.
- Internal-only capital question: abstained as intended without general fallback.
- Latest Python: returned a live-source requirement rather than a current answer.
- Current US president: initially echoed the question while claiming answer readiness. The final code expands Persian freshness wording and rejects question echoes. A real repeat after restart returned `needs_live_source`; the earlier failure is retained.
- Private organization key: refused before inference.

The separate [corrected live run](routing-live-v07-corrected.json) also tested simple addition: the final system rejected the model output as invalid rather than presenting a result. No claim that this model is reliably capable of arithmetic is made.

## Current-information check

The development assistant independently consulted [Python.org](https://www.python.org/downloads/) and the [White House administration page](https://www.whitehouse.gov/administration/) while reviewing the tests. These checks are in `routing-review-v07.json`. They were **not** provided to the runtime model and are not an online capability of the demo. Current-information questions therefore remain unanswered without a live retrieval integration.

## Regression evidence and limits

76 unit/API tests passed. Tests cover citation separation, internal-only/model-only routing, credential refusal, forced fresh-source behavior even when a mock model asserts a stale answer, unknown modes, invalid grounded output, and echoed questions. The original 24-case runbook gate remains 22/24. Unit tests verify software behavior, not world knowledge accuracy.

The interface warns about actual general-knowledge failures of this small model. The two factual failures are not fixed by origin labels or exact-quote checks. A stronger model and independently authored factual evaluation are required before presenting open-domain answers as reliable. The eight initial cases and two later cases are development probes, not a representative benchmark. No aggregate accuracy score is advertised.

This report records the local development run from 2026-10-22. The v0.7 implementation and original evidence are published together; see PUBLICATION_2026-11-01.md for the publication recheck. A development server is not guaranteed to remain active.

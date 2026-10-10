# Local model experiment — 8 October 2026

Qwen3-0.6B-Q8_0, official Qwen GGUF, llama.cpp b11476 Windows CPU, four threads, context 2048. Source identity and file hash are recorded in the JSON report. CPU model inference has no metered API cost.

Initial free-form trials were poor: one returned metadata instead of a Persian answer, another produced awkward/unsupported wording. Those outputs remain in local-model-initial.json and local-model-freeform-followup.json. No broad quality claim is warranted.

The final mode uses the language model to select numbered sentences and displays exact source text. The printer and VPN smoke cases returned source sentences in 3.44s and 3.28s, with 40 and 44 generated tokens. An unrelated gold-price question abstained before inference. These are small, developer-selected smoke cases after prompt changes, not a held-out evaluation. One earlier injection-style question was rejected by lexical retrieval; that is not evidence of model-level injection resistance.

39 automated tests passed on 9 October, including six new regression-gate tests. The original 33 tests cover, including invalid indices/IDs, malformed selections, token truncation, busy/disabled/timeout behavior, public/staff separation, and the HTTP draft route. The ordinary tests mock generation to avoid model download or token use; the JSON smoke report contains actual inference. Browser visual validation remains pending.

The added model does not improve baseline retrieval recall. It cannot retrieve a source missed by BM25, and sentence selection can omit qualifications or choose irrelevant text. Users must inspect the complete guide. All documents are synthetic.

The latest real POST /api/draft integration returned a source-exact draft in 4.34s (235 input + 40 output tokens) on 9 October; see local-model-http.json. The launcher started and served that request, but the external Windows test harness timed out during process-tree cleanup. This is not a successful end-to-end shutdown test. Browser visual validation and interactive Ctrl+C shutdown remain unverified.

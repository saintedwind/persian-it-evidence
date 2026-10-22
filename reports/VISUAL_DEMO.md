# Graphical evidence desk

Run `python server.py`, then open **http://127.0.0.1:8765/demo**. On Windows, `run-visual-demo.ps1` launches the same server. Stop it with Ctrl+C. There are no new dependencies or service credentials.

The separate demo route uses the existing `/api/documents` and `/api/ask` endpoints. It defaults to six real, attributed Persian Wikipedia extracts with frozen revision URLs and their existing CC BY-SA attribution. A selector also exposes the synthetic support-guide collection, explicitly labeled as examples. The main handbook remains at `/`.

The interface includes a document catalog, suggested questions, a visual processing path, the returned source-exact text, ranked source cards, source dialogs, and a receipt with method/corpus/text hashes. No generated or prerecorded answer is substituted for a request. The path is a UI representation of one real server request, not instrumentation of four separately timed backend services. The displayed duration is measured browser request round-trip time, not model latency.

The current engine mode is extractive BM25. This demo does not invoke a generative language model. A lack of sufficient retrieval evidence produces an explicit abstention instead of fabricated prose. Ranking scores are not confidence probabilities. Reference articles are historical snapshots, not a live information feed or organizational instructions.

## Actual verification

- 55 unit/API tests passed, including the new route/CSP test and source-exact DNS receipt check.
- Existing 24-question evaluation gate passed unchanged: 22/24 correct source or abstention.
- Four additional real HTTP requests passed; full response evidence is in `visual-demo-checks.json`.
- Browser interaction verified reference browsing, phishing retrieval, source dialog/link, abstention, sample printer retrieval, collection switching, and the expanded receipt.
- A 390px mobile viewport was inspected with no horizontal overflow (375px document width excluding the scrollbar). Desktop and mobile screenshots were captured from the actual running application.
- Existing request cancellation and new collection/catalog sequence checks prevent late results from rendering into a different collection. Response text uses textContent rather than HTML insertion; links admit only the existing canonical Wikipedia revision URL format.

Screenshots: [desktop](rag-demo-desktop.png), [answer](rag-demo-answer.png), [mobile](rag-demo-mobile.png).

These checks do not establish broad answer accuracy, organization authentication, or complete accessibility conformance. Browser fault-injection and a full keyboard-only acceptance pass were not performed in this run. The demo runs locally; its code and recorded evidence are included in this repository. This is not a publicly hosted service.

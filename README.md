# دفتر پشتیبانی

A Persian support handbook: find a runbook, inspect its source, and prepare a support ticket when the issue remains unresolved.

**v0.3 — local working prototype.** The 12 public runbooks are synthetic examples, not an organization's approved procedures. Questions are not stored and ticket drafts are not submitted.

## Run

Requires Python 3.11+, with no package installation or service credentials.

```sh
python server.py
# Open http://127.0.0.1:8765
python -m unittest discover -s tests -v
python evaluate.py --check
```

## What changed

- Browse a public guide directory and open documents directly.
- Search in Persian, inspect ranked results, and select a source text.
- Copy a guide with its identifier or prepare an editable ticket with problem, device, error, reproduction steps and guide consulted.
- Keyboard navigation, a search shortcut, request timeout, and protection against stale search responses.
- An ink-and-paper layout using the locally bundled Gandom typeface. Font copyright and license are preserved in `web/Gandom-LICENSE.txt`; upstream: https://github.com/rastikerdar/gandom-font.

## Retrieval and access

Persian normalization and tokenization feed a BM25 ranker. A fixed lexical-coverage heuristic determines whether to show a result. Text is displayed verbatim; relevance is not a guarantee that a procedure solves the issue.

Public access is enforced before scoring and before building the directory. The browser cannot request a staff role. The CLI's `--scope staff` is a trusted local test switch, not authentication.

| Endpoint | Behavior |
|---|---|
| `GET /health` | Process health |
| `GET /api/documents` | Public directory |
| `GET /api/documents?id=IT-004` | Public document, or 404 for absent/restricted IDs |
| `POST /api/ask` | JSON containing only `question`; ranked excerpts and status |
| `POST /api/draft` | Explicit optional local sentence selection; bounded question and output |

The browser creates ticket drafts locally. Clipboard permission depends on the browser; text remains selectable when automatic copying is unavailable.

## Validation

The v0.3 suite contains 39 unit/API tests, all passing locally on 9 October 2026. Tests cover input validation, public-only access, source-exact selection, malformed/truncated model output, concurrency and regression-gate failures. Model calls in unit tests are mocked. Actual inference evidence is recorded separately below. Browser layout and end-to-end interaction checks remain pending.

The unchanged 24-question synthetic benchmark contains 18 answerable and 6 unanswerable cases:

| Metric | Result |
|---|---:|
| Recall@3 on answerable questions | 16/18 = 88.9% |
| MRR@3 | 0.889 |
| Correct source or abstention | 22/24 = 91.7% |
| Abstention on unanswerable questions | 6/6 |

See `reports/evaluation.json` and `reports/FAILURE_ANALYSIS.md`. These author-written smoke tests are not an independent holdout or a production accuracy estimate. Two paraphrase failures remain; interface changes do not improve the retrieval score.

The regression gate now preserves each of the 22 previously passing cases, including all six abstentions. Known failures remain in the dataset and may improve. An aggregate score cannot hide a newly broken case.

## Review the implementation

- [Case study: workflow, decisions and measured results](reports/CASE_STUDY.md)
- [Operator notes: start, troubleshoot, test and hand off](reports/OPERATIONS.md)
- [Known retrieval failures](reports/FAILURE_ANALYSIS.md)

## Limits

The corpus has 12 public examples and one synthetic restricted fixture. Indirect wording can fail; topic words can also retrieve an irrelevant procedure. There is no organization login, ingestion workflow, document approval, editing service or ticket-system integration. The standard-library HTTP server binds to loopback and is intended for local use, not public deployment. No customer adoption or savings are claimed.

Maintained by Peyman Gholamhosseini. Independent project; not an Azarab product or deployment.


## Optional local model (v0.3 experiment)

A real Qwen3-0.6B-Q8_0 model runs through llama.cpp on CPU. No paid API, key, or cloud inference is used. Download the official [model](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/23749fefcc72300e3a2ad315e1317431b06b590a) (~640 MB) and [Windows CPU runtime b11476](https://github.com/ggml-org/llama.cpp/releases/tag/b11476), then run:

```sh
python run_local.py --runtime /path/to/llama-server.exe --model /path/to/Qwen3-0.6B-Q8_0.gguf
```

The application is at http://127.0.0.1:8765. The new button explicitly requests a source-based draft. Ordinary search never calls the model. Ctrl+C stops both processes. Plain `python server.py` retains the original search-only mode. Model files are excluded from Git.

The small model's free-form Persian output was unreliable in initial trials. The implemented mode asks it to select numbered source sentences, then renders those sentences verbatim in source order. This is real language-model inference for selection, not free-form answer generation. Selection may still be incomplete or irrelevant; consult the full source.

Limits: 400-character question, one public source up to 1,800 characters, 2,048-token runtime context, 96 output tokens, one inference at a time, 90-second timeout, no automatic retries. Invalid source IDs, sentence indices, duplicate selections and truncated outputs produce no draft. Unknown questions skip inference. The endpoint is fixed to loopback and bypasses proxy settings.

See `reports/local-model-smoke.json` for actual inference results and `reports/LOCAL_MODEL.md` for limitations. Earlier free-form failures remain in separate reports. No organization data was used. Model license: Apache-2.0; runtime license: MIT, retained with their distributions. Download bandwidth, disk, RAM and electricity are still required.

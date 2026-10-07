# دفتر پشتیبانی

A Persian support handbook: find a runbook, inspect its source, and prepare a support ticket when the issue remains unresolved.

**v0.2 — local working prototype.** The 12 public runbooks are synthetic examples, not an organization's approved procedures. Questions are not stored and ticket drafts are not submitted.

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

The browser creates ticket drafts locally. Clipboard permission depends on the browser; text remains selectable when automatic copying is unavailable.

## Validation

The v0.2 suite contains 23 unit/API tests covering input validation, normalization, exact source text, access isolation, directory routes, restricted document lookup, and font delivery. All 23 tests passed locally on 7 October 2026. Run the commands above to reproduce the checks. Browser layout and end-to-end interaction checks are pending: the local browser preview was unavailable in the build environment.

The unchanged 24-question synthetic benchmark contains 18 answerable and 6 unanswerable cases:

| Metric | Result |
|---|---:|
| Recall@3 on answerable questions | 16/18 = 88.9% |
| MRR@3 | 0.889 |
| Correct source or abstention | 22/24 = 91.7% |
| Abstention on unanswerable questions | 6/6 |

See `reports/evaluation.json` and `reports/FAILURE_ANALYSIS.md`. These author-written smoke tests are not an independent holdout or a production accuracy estimate. Two paraphrase failures remain; interface changes do not improve the retrieval score.

## Limits

The corpus has 12 public examples and one synthetic restricted fixture. Indirect wording can fail; topic words can also retrieve an irrelevant procedure. There is no organization login, ingestion workflow, document approval, editing service or ticket-system integration. The standard-library HTTP server binds to loopback and is intended for local use, not public deployment. No customer adoption or savings are claimed.

Maintained by Peyman Gholamhosseini. Independent project; not an Azarab product or deployment.

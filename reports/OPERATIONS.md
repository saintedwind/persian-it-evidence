# Run and review the handbook

## Search-only mode

From the repository root, run `python server.py` with Python 3.11 or later. Open http://127.0.0.1:8765. No package installation or model download is needed for search.

Try `صف چاپ پرینتر متوقف شده`: inspect source IT-004. Try an unrelated question: expect an insufficient-evidence response. Open the directory and inspect a guide before preparing a ticket. The editable ticket stays in the page; copying does not submit it to a help desk.

## Optional sentence selection

Follow the pinned model/runtime links in the README and run `python run_local.py --runtime PATH --model PATH`. This starts the local runtime on port 8081 and the application on 8765. Use only public demonstration text. The full model download is about 640 MB and is not included in this repository.

If startup fails, check that both supplied files exist and ports 8081/8765 are free. Do not terminate an unrelated process occupying a port. The launcher waits at most 90 startup probes; inference has a 90-second timeout. A busy request is not queued or retried. A failed or truncated response produces no draft; use the original source instead.

Ctrl+C stops the launcher and its model child. Closing an unrelated terminal is not a supported shutdown workflow. Do not expose either port to the Internet: the standard-library server is for local review and has no organizational authentication.

## Before changing search or sources

Run `python -m unittest discover -s tests -v` and `python evaluate.py --check`. The latter writes `reports/evaluation.json` and compares successful cases with `data/regression-baseline.json`. Do not weaken the baseline to make a failing change pass. Keep the two known paraphrase failures visible; use a separately frozen test set for new retrieval approaches.

The unit suite does not need the model and does not measure its answer quality. Real inference reports are small local observations, not a latency guarantee. Browser layout and interaction verification must be reported separately from API tests.

## Data and handoff

Questions are not persisted by application access logs; they exist in memory during processing. The optional model receives one public source over loopback with proxies bypassed. Runtime, browser and operating-system behavior are outside this application's logging guarantee. No customer documents, credentials or account data belong in the demonstration corpus.

For a pilot handoff, record a document owner, approval date, access policy, rollback commit, test results, and support contact. None of these organizational approvals is supplied by this prototype.

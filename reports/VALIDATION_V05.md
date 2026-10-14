# Persian retrieval validation, 2026-10-14

## Tested behavior

53 unit/API tests passed. The previous 22 successful golden decisions and all six original abstentions remain. The default application is lexical and requires no dependencies. Optional multilingual mode uses actual CPU inference of a pinned, quantized MiniLM model, not mock embeddings. Browser acceptance covers prior ticket/draft lifecycle behavior and a new six-document Persian reference collection, original revision links, displayed source hashes and mobile overflow.

| Set | Lexical correct | Hybrid correct | Hybrid unsupported abstentions |
|---|---:|---:|---:|
| Original synthetic | 22/24 | 22/24 | 6/6 |
| Persian transfer | 24/48 | 40/48 | 12/12 |
| Actual public reference extracts | 34/36 | 35/36 | 6/6 |

Raw results: semantic-v05.json. Actual loopback HTTP: live-semantic-v05.json, 108 queries, every returned text receipt reconciled with its answer/source. Browser screenshots/results: ui/. Model file download sizes: 235052644 and 17083009 bytes, both SHA-256 verified. No paid provider endpoint or organization data was used.

## Experimental history and leakage limits

The additional 72 synthetic questions (24 development, 48 transfer) and 36 real-source questions were authored before first neural output. Initial conservative semantic screening did not improve results; retained in semantic-v05-initial.json. An initial missing-facet guard improved transfer source decisions but falsely accepted one STAFF/DR42 request as a public software guide; retained in semantic-v05-facet-iteration.json. No restricted text was disclosed. Exact opaque-ID matching was then added to lexical and semantic paths, removing that acceptance. This third iteration uses the development-selected 0.40 cosine and 0.08 runner-up margin.

Because transfer outputs informed guard development, this is an inspected regression/transfer set, NOT an untouched holdout. Threshold selection uses development cases only, but that does not erase development exposure. An independent human-authored evaluation is still needed. Similarity and source-selection scores do not establish complete semantic entailment, procedure safety or customer accuracy.

## Remaining failures

Original q17 (paper not coming out) and q18 (other party cannot hear) still abstain. Eight transfer positives still abstain. The reference question about connecting company branches over a public network returns Wi-Fi instead of VPN; this failure is retained rather than tuned away. Optional mode therefore remains experimental, with lexical mode the default.

Only six encyclopedic introductions and twelve synthetic runbooks are present. No PDF/OCR ingestion, operational approval process, independent question author, production latency/load guarantee, enterprise authentication or tenant isolation is claimed. Model inputs truncate at 128 tokens. A text digest is not a statement of publisher authority or factual currency.

## Reproduction

Run the commands in README; ordinary tests run without model dependencies. prepare_semantic.py downloads immutable, hashed files only on explicit invocation. evaluate_semantic.py records the development grid, selected thresholds, raw decisions and environment. live_semantic.py serves real local HTTP on an ephemeral loopback port and stops its server afterward. tests/ui.cjs uses isolated browser state, never the user's browser profile. Native Chrome was used for local browser testing; CI uses Chromium. No browser script/model responses count as real language-generation evaluation.

## Independent GitHub validation

[Run 31](https://github.com/saintedwind/persian-it-evidence/actions/runs/38568779781) completed successfully for code revision `fe9ac63f66a5fec26d5fd1e00675c54b2d785238`: unit/API job 8s, real neural/HTTP job 28s, Chromium job 38s. The obsolete upload-artifact runtime warning was removed by upgrading to v7. Documentation-only changes after this revision do not alter tested code.

[Neural evidence bundle](https://github.com/saintedwind/persian-it-evidence/actions/runs/38568779781/artifacts/11896478892), SHA-256 `a0a536bc417d74f73a2ae75eb5f26ae74d18b10063d32edc6536e13538c43e70`. [Browser evidence bundle](https://github.com/saintedwind/persian-it-evidence/actions/runs/38568779781/artifacts/11896752437), SHA-256 `8705b5afae2113955006c3a63776101b780cbb73d4aed120a54ae6cbacc94116`. CI artifacts have finite retention; checked-in results and local screenshots remain in reports. Published byte digests of all six reference texts were compared against the manifest. Original sample source documents were not rewritten to match benchmark questions.

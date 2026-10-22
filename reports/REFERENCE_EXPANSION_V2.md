# Reference expansion v2 — 2026-10-22

The active local reference collection grew from six to **34 real Persian Wikipedia introductions**: 28 additions, six byte-identical preserved originals. There are 42,315 source characters, not 34 complete articles. No source text was synthesized or rewritten. Frozen encyclopedia text is not an approved organizational procedure or live information feed.

| Topic | Sources |
|---|---:|
| شبکه | 12 |
| ارتباطات | 4 |
| امنیت | 10 |
| سیستم‌ها | 4 |
| داده | 2 |
| سخت‌افزار | 2 |

## Ingestion and provenance

`data/reference-expansion-plan.json` records the curated topic list and search aliases. `prepare_reference.py --output NEW_STAGING_DIRECTORY` downloads into staging only; `--resume` keeps successful downloads. It follows redirects, rejects missing/disambiguation/undersized/duplicate content, bounds response sizes, and handles upstream rate limits with a delayed retry. It never silently modifies the active collection. Review staged content before activation.

Each added text has a canonical title, original request title, article/revision identity, immutable source URL, contributor-history link, license, timestamp, category, text checksum and raw API receipt checksum. `data/reference-receipts/` contains the 28 original API responses. The loader checks the receipt bytes, revision, title and exact extract against every new source file. Hashes establish byte integrity, not factual correctness. The old manifest is archived in `reports/reference-v1-manifest.json`; text authorship and CC BY-SA 4.0 licensing are retained separately from the code license.

Two planned sources were excluded: the requested backup page was missing and the short RAID title resolved to a disambiguation page. These failures are preserved in the active manifest; no fabricated replacement was added. Backup coverage remains a known gap.

## Retrieval checks and observed regressions

The 18 new authored development probes were frozen before expanded-corpus retrieval. **17/18** passed; the failed probe asks for the excluded backup source. These are functional development checks, not an independent user benchmark.

The original 36 reference probes initially fell from 34/36 to 32/36 when more documents competed. Both initial failures and the corrected run are retained. The fix normalizes Persian/Arabic digits and matches explicit dotted technical identifiers, preventing IEEE 802.11 from being confused with other standards. A narrow guard abstains on requests for organization-owned private credential values. It is not a general privacy or intent classifier. The corrected result is **34/36**, preserving all formerly passing reference probes. Two older reference failures remain.

The unrelated 24-case synthetic-runbook regression gate remains **22/24**. **60 unit/API tests** passed. Four additional real loopback HTTP checks validated ransomware, DHCP, the IEEE standard and private-key abstention. Returned text hashes match the selected sources. No language-model inference or paid API was used.

## Interface

`/demo` now offers a bounded, scrollable catalog with title/topic filtering, categories, source license and receipt timestamps. The browser test filtered 10 security sources out of 34 and retrieved the real ransomware source. The original handbook also uses the expanded collection. The application runs locally; source and recorded evidence are included in this repository.

Evidence: `reference-expansion-v2-evaluation.json` (initial), `reference-expansion-v2-guarded-evaluation.json` (corrected), `reference-expansion-v2-comparison.json` (initial historical comparison), and `reference-expansion-v2-acceptance.json` (actual HTTP and inventory checks).

## Limits

All 34 sources are from one encyclopedia publisher. Multi-publisher triangulation and vendor-approved operational instructions are not implemented. Facts were not independently verified, semantic-retrieval evaluation was not repeated on this larger corpus, and no claim of enterprise readiness is made. User questions still execute locally against frozen stored text, without online browsing.

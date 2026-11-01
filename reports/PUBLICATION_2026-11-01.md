# Publication audit — 2026-11-01

## Scope

Three answer modes, explicit answer origin, uncited model fallback, recognized current-fact abstention and source/citation separation.

## Validation

76 unit/API regression tests passed again on 2026-11-01.

The first pull-request run exposed a client-side race in the chunked-request boundary test: urllib could raise BrokenPipeError while the server correctly rejected the headers early. The test now sends headers with HTTPConnection and asserts the exact HTTP 400 response and that the model was not invoked. The server's rejection policy is unchanged. The corrected case passed 50 consecutive local repetitions; the full 76-test suite passed again. The original failed Actions run is retained: https://github.com/saintedwind/persian-it-evidence/actions/runs/41333650440.

Actual Qwen3-1.7B CPU HTTP experiments are dated 2026-10-22; original failed general-knowledge cases and corrected guard runs are preserved.

[Original evidence and limitations](ANSWER_ROUTING_V07.md)

## Limitations retained

The small model gave a fabricated Japanese capital and incorrect atmospheric explanation. Origin labels do not fix factual accuracy. No live web access, reliable general knowledge, general authorization system or production deployment is claimed.

## Publication boundary

Source and selected attributed evidence only. No credentials, private documents, raw downloaded evaluation inputs, model weights, local databases, caches or temporary runtime state are published. Historical experiments are not renamed as fresh validation. No production/customer accuracy claim is added.

Pre-publication main revision: `b00b24f3a3c64574c1d72d53e4f8f966fdf549dc`. GitHub Actions on the published source is the independent CI record; a historical green run is not substituted for a new code revision.

# Publication audit — 2026-11-01

## Scope

Three answer modes, explicit answer origin, uncited model fallback, recognized current-fact abstention and source/citation separation.

## Validation

76 unit/API regression tests passed again on 2026-11-01.

Actual Qwen3-1.7B CPU HTTP experiments are dated 2026-10-22; original failed general-knowledge cases and corrected guard runs are preserved.

[Original evidence and limitations](ANSWER_ROUTING_V07.md)

## Limitations retained

The small model gave a fabricated Japanese capital and incorrect atmospheric explanation. Origin labels do not fix factual accuracy. No live web access, reliable general knowledge, general authorization system or production deployment is claimed.

## Publication boundary

Source and selected attributed evidence only. No credentials, private documents, raw downloaded evaluation inputs, model weights, local databases, caches or temporary runtime state are published. Historical experiments are not renamed as fresh validation. No production/customer accuracy claim is added.

Pre-publication main revision: `b00b24f3a3c64574c1d72d53e4f8f966fdf549dc`. GitHub Actions on the published source is the independent CI record; a historical green run is not substituted for a new code revision.

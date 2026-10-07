# Failure analysis — v0.1

Evaluation date: 2026-10-07. Source: `evaluation.json`, 24 synthetic author-written cases.

## Observed failures

| ID | Question | Expected source | Observed behavior |
|---|---|---|---|
| q17 | برگه ها از دستگاه بیرون نمی آیند | IT-004 printer runbook | No accepted source; lexical retrieval misses the paraphrase |
| q18 | موقع مکالمه طرف مقابل چیزی نمی شنود | IT-006 VoIP runbook | No accepted source; lexical retrieval misses the paraphrase |

These two cases remain in the dataset. Adding their exact words to document tags would improve the displayed score while making the evaluation less informative; that change was deliberately not made.

## What the results do and do not establish

- Most direct topic queries work on the tiny synthetic corpus.
- The restricted document was not retrieved by public queries tested here. This does not prove enterprise security.
- All six unanswerable questions abstained in this dataset. This does not mean the coverage heuristic rejects all unsupported or adversarial questions.
- An exact source excerpt cannot hallucinate new wording, but it can still be irrelevant, outdated, incomplete, or wrong.
- No generative answer was evaluated. The score is source-selection/abstention agreement, not answer factuality.
- Latency in the JSON is a single local observation; it is not comparable cloud throughput or a service-level commitment.

## Next controlled experiment

Freeze v0.1 and its data. Add multilingual embeddings as a separately selectable retriever. Create a new paraphrase-heavy set with at least 60 questions, answer spans, unanswerable counterexamples, and conflicting-document cases. Split tuning and evaluation before changing thresholds. Where possible, have another person write/review questions without seeing retriever output. Report the lexical baseline and semantic retriever on the same frozen test set, including regressions, model revision, hardware, and license. Add an LLM only after retrieval quality and citation checks are measurable.

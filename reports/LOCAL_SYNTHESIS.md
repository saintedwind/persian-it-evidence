# Local language-model synthesis

The graphical evidence desk now supports an explicit **ساخت پاسخ مستند** button after a successful source lookup. The model writes a Persian draft from the selected source. The original source, revision URL and full text remain separately visible. This is distinct from the older sentence-selection `/api/draft` experiment.

## Running

With the official, locally verified Qwen3-1.7B Q8_0 weights and a compatible llama.cpp server executable:

```sh
python run_with_answer.py --runtime /path/to/llama-server --model /path/to/Qwen3-1.7B-Q8_0.gguf
# Open http://127.0.0.1:18765/demo
```

The launcher verifies weight SHA-256 `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`, refuses occupied ports, binds both services to loopback, and owns/stops only the child it started. Ctrl+C stops both services. An optional fresh `--stop-file PATH` supports graceful automation shutdown. Running `python server.py` still provides retrieval without enabling model synthesis. No new Python dependencies, API keys or paid inference are required; model weights are not bundled with the repository.

Official model: https://huggingface.co/Qwen/Qwen3-1.7B-GGUF , revision `90862c4b9d2787eaed51d12237eafdfe7c5f6077`. Actual runtime: llama.cpp b11476, CPU, four threads, 8192-token context, one slot, output capped at 384 tokens.

## Request contract

`POST /api/answer` accepts the same `question` and `collection` fields as retrieval, with a stricter 400-character question limit. It first retrieves a public source. Without accepted evidence it returns `insufficient_evidence` without invoking a model. Inputs are never forwarded through an environment proxy, redirects are disabled, and only the explicit IPv4 loopback completions endpoint is allowed. A single-request semaphore bounds simultaneous generation; busy, timeout, invalid/truncated output and unavailable-model states are distinct from success.

Generation receives one selected source, not the entire corpus. Sources longer than 8000 characters are refused rather than silently truncated. Output must contain an answer, matching source ID, boolean support flag and a 20–300-character exact quote. The server checks source identity and quote membership. It rejects malformed, incomplete or fabricated-quote results instead of displaying them. Model text is inserted as plain text. Client cancellation/sequence checks keep late output from appearing after a new search or collection switch; cancellation does not guarantee that already-running CPU inference has stopped.

## Actual evidence

`local-answer-live.json` records five real HTTP probes. Three invoked the local model and produced accepted Persian drafts: phishing, ransomware and DHCP. Two requests—an unrelated concert-price question and a request for an organization's private key—abstained before inference. The private-key guard and evidence threshold are narrow heuristics, not general intent or security classification.

66 unit/API tests passed, including source/quote mismatch rejection, no-inference abstention, disabled/offline model, truncated output handling and remote-endpoint rejection. Unit model calls are mocked; the separate live record contains actual inference usage and durations. These five authored development probes are not a held-out accuracy or safety benchmark.

## Limits

Exact quotation membership does **not** establish that all generated claims follow from the quote. The displayed answer is labeled as a model-written draft requiring review. On manual inspection, phishing and ransomware drafts captured the source's main definition; the DHCP answer was grammatical enough to display but imprecise and incomplete about its purpose. No claim of perfect Persian, full entailment, instruction-injection resistance or production reliability is made. Long generation time on CPU remains possible. Retrieval is local against frozen sources; this is not live web research.

The running demonstration intentionally retains its owned model process so the user can try it. Source, configuration and recorded evidence are included in this repository.

Pinned weight file: https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/90862c4b9d2787eaed51d12237eafdfe7c5f6077/Qwen3-1.7B-Q8_0.gguf . Download it separately; the launcher checks its full checksum before execution. No credentials or private configuration are stored in this repository.

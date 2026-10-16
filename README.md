# agent-core

A minimal LLM client built on LiteLLM: one `chat()` function that works with any provider and returns the answer, input/output tokens, cost in USD and latency in ms. Temporary provider errors (429/503) are retried automatically.

**Setup:** `pip install -r requirements.txt`, then set your provider key (e.g. `GEMINI_API_KEY` or `ANTHROPIC_API_KEY`).

**Run:** `python -m agent_core.llm "hello"`

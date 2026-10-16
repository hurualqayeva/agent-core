import sys
import time

import litellm


def chat(messages, model="gemini/gemini-3.8-flash"):
    start = time.perf_counter()
    response = litellm.completion(model=model, messages=messages, num_retries=3)
    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "text": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "cost_usd": litellm.completion_cost(completion_response=response),
        "latency_ms": round(latency_ms),
    }


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "hello"
    result = chat([{"role": "user", "content": prompt}])
    for key, value in result.items():
        print(f"{key}: {value}")
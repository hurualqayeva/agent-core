import json
import re
import sys
from pathlib import Path

import litellm

MODEL = "gemini/gemini-3.8-flash"
FALLBACKS = ["gemini/gemini-2.5-flash-lite"]
MAX_STEPS = 8
DATA_DIR = Path("data").resolve()


def calculator(expression):
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression) or "**" in expression:
        return "error: only numbers and + - * / ( ) are allowed"
    return eval(expression, {"__builtins__": {}})


def read_file(path):
    file = (DATA_DIR / path).resolve()
    if not file.is_relative_to(DATA_DIR):
        return "error: you may only read files inside ./data"
    if not file.is_file():
        return f"error: file not found: {path}"
    return file.read_text(encoding="utf-8")


TOOLS = {"calculator": calculator, "read_file": read_file}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression, e.g. '1200 + 1350'.",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string"}},
                       "required": ["expression"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the data folder, e.g. 'sales.csv'.",
        "parameters": {"type": "object",
                       "properties": {"path": {"type": "string"}},
                       "required": ["path"]}}},
]


def run_agent(question, model=MODEL):
    messages = [
        {"role": "system", "content": "Answer using the tools. Files are in the data folder. "
                                      "Use the calculator for any arithmetic."},
        {"role": "user", "content": question},
    ]
    for step in range(1, MAX_STEPS + 1):
        response = litellm.completion(model=model, messages=messages, tools=TOOL_SCHEMAS,
                                      num_retries=3, fallbacks=FALLBACKS)
        message = response.choices[0].message
        if not message.tool_calls:
            print(f"final answer: {message.content}")
            return message.content
        messages.append(message)
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            try:
                result = TOOLS[name](**args)
            except Exception as error:
                result = f"error: {error}"
            print(f"{step} | {name} | {args} | {result}")
            messages.append({"role": "tool", "tool_call_id": call.id,
                             "name": name, "content": str(result)})
    print("stopped because: max steps")


if __name__ == "__main__":
    run_agent(" ".join(sys.argv[1:]) or "What is total revenue for Q3?")
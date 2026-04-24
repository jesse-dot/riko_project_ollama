# Local Ollama chat integration with history
import json
import os
from urllib import request
from urllib.error import HTTPError, URLError

import yaml

with open('character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

# Constants
HISTORY_FILE = char_config['history_file']
MODEL = char_config.get('model', 'llama3.1')
OLLAMA_BASE_URL = char_config.get('OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
SYSTEM_PROMPT_TEXT = char_config['presets']['default']['system_prompt']
SYSTEM_PROMPT = [{"role": "system", "content": SYSTEM_PROMPT_TEXT}]


def _extract_content_as_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts).strip()

    return ""


def _normalize_history(messages):
    normalized = []
    for msg in messages:
        if not isinstance(msg, dict):
            continue

        role = msg.get("role")
        if role not in {"system", "user", "assistant"}:
            continue

        text = _extract_content_as_text(msg.get("content"))
        if text:
            normalized.append({"role": role, "content": text})

    if not normalized or normalized[0].get("role") != "system":
        return SYSTEM_PROMPT + normalized

    return normalized


# Load/save chat history
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                return SYSTEM_PROMPT.copy()
            return _normalize_history(history)
    return SYSTEM_PROMPT.copy()


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_riko_response_no_tool(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    req = request.Request(
        url=f"{OLLAMA_BASE_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=120) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        details = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Ollama request failed with status {e.code}: {details}") from e
    except URLError as e:
        raise RuntimeError(
            f"Could not connect to Ollama at {OLLAMA_BASE_URL}. Ensure Ollama is running."
        ) from e

    message = response_data.get("message", {})
    content = message.get("content")
    if not content:
        raise RuntimeError("Ollama response did not include message content.")
    return content


def llm_response(user_input):
    messages = load_history()

    # Append user message to memory
    messages.append({
        "role": "user",
        "content": user_input
    })

    riko_test_response = get_riko_response_no_tool(messages)

    # Append assistant message to history.
    messages.append({
        "role": "assistant",
        "content": riko_test_response
    })

    save_history(messages)
    return riko_test_response


if __name__ == "__main__":
    print('running main')

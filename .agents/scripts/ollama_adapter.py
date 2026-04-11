import json
import urllib.request
import os
import sys

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

"""
Ollama Adapter for AntiGravity Agents (Native API v2)
Connects to local Gemma4:26B via native API on localhost:11434.
"""

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_ID = "prutser/gemma-4-26B-A4B-it-ara-abliterated:Q3_K_M"

def strip_thinking(text: str) -> str:
    """Strip <think>...</think> block from model output and return only the answer."""
    import re
    # Remove everything inside <think>...</think> (including the tags)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

def query_ollama(prompt, system_prompt="You are a helpful assistant.", max_tokens=2048):
    data = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.1,
            "top_p": 0.9,
            "num_ctx": 16383,
            "stop": ["</think>", "<|end_of_turn|>"]
        }
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(OLLAMA_API_URL, data=json.dumps(data).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            message = res_data.get("message", {})
            content = message.get("content", "")
            thinking = message.get("thinking", "")
            
            # If the model is a 'Thinking' model, Ollama might separate the reasoning.
            # We prioritize the final answer (content), but fall back to 'thinking' 
            # if content is empty (common in some reasoning-heavy configurations).
            if not content.strip() and thinking.strip():
                return strip_thinking(thinking)
            
            return strip_thinking(content)
    except Exception as e:
        return f"Error querying Ollama Native API: {str(e)}"

def summarize_file(file_path):
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"Reading error: {str(e)}"
    
    # Context window management (approx 32k tokens)
    MAX_CHARS = 120000 
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + "\n... (omitted due to length)"
    
    prompt = (
        "Summarize the following source code for a developer. "
        "List the key responsibilities, main functions, and any notable patterns or issues. "
        "Be concise and use bullet points.\n\n"
        f"{content}"
    )
    system_message = (
        "You are an expert Python developer reviewing code for a Monster Hunter equipment management app. "
        "Always respond in English with clear, structured bullet points."
    )
    
    return query_ollama(prompt, system_message)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ollama_adapter.py <action> [args]")
        print("Actions: summarize <path>, query <prompt>")
        sys.exit(1)
    
    action = sys.argv[1]
    if action == "summarize":
        print(summarize_file(sys.argv[2]))
    elif action == "query":
        print(query_ollama(sys.argv[2]))

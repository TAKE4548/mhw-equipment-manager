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
Optimized for Qwen3:14b (32k context support)
"""

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_ID = "qwen3:14b"

def strip_thinking(text: str) -> str:
    """Strip <think>...</think> block from model output and return only the answer."""
    import re
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
            "num_ctx": 32768  # Support for Qwen3:14b 32k context
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
            
            # Universal handling: Use content if available, fallback to thinking field
            final_text = content if content.strip() else thinking
            return strip_thinking(final_text)
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
    
    # Qwen3:14b 32k allows for larger file chunks (approx 100k chars)
    MAX_CHARS = 100000 
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + "\n... (omitted due to length)"
    
    prompt = (
        "Analyze the following source code for a developer. "
        "Summarize its purpose, core logic, and key data structures. "
        "Point out any technical debt or potential improvements. "
        "Respond in Japanese with professional tone.\n\n"
        f"{content}"
    )
    system_message = (
        "You are an expert Python engineer specialized in Monster Hunter equipment management systems. "
        "Provide a high-quality, technical summary."
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

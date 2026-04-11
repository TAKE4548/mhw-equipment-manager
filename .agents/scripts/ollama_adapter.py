import json
import urllib.request
import os
import sys

"""
Ollama Adapter for AntiGravity Agents
Connects to local Gemma4:26B via OpenAI-compatible API on localhost:11434.
"""

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL_ID = "gemma4:26b"

def query_ollama(prompt, system_prompt="You are a helpful assistant.", max_tokens=2048):
    url = f"{OLLAMA_BASE_URL}/chat/completions"
    data = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def summarize_file(file_path):
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple chunking if content is extremely large (v1 implementation)
    # Target 32k tokens (approx 120k characters for English, lower for Japanese)
    MAX_CHARS = 100000 
    if len(content) > MAX_CHARS:
        content = content[:MAX_CHARS] + "\n... (omitted due to length)"
    
    prompt = f"Please summarize the following content in Japanese, highlighting the key points for a developer:\n\n{content}"
    system_message = "You are an expert developer assistant specialized in Monster Hunter project maintenance."
    
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

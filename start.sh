#!/bin/bash
# curl -fsSL https://ollama.com/install.sh | sh
# OLLAMA_HOST=0.0.0.0 ollama list

# Run the ollama command
OLLAMA_HOST=0.0.0.0 ollama list && ollama server && ollama run llama3

python /repo-copilot/repo_documentation/app.py
python /repo-copilot/setup_workflow.py
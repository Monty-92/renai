#!/bin/bash
# Copyright 2024 Renai Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

OLLAMA_HOST="${OLLAMA_HOST:-localhost}"
OLLAMA_PORT="${OLLAMA_PORT:-11434}"
OLLAMA_URL="http://${OLLAMA_HOST}:${OLLAMA_PORT}"

echo "======================================"
echo "Renai Model Pull Script"
echo "======================================"
echo ""
echo "Ollama URL: $OLLAMA_URL"
echo ""

# Check if Ollama is running
echo "Checking Ollama connection..."
if ! curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "Error: Cannot connect to Ollama at $OLLAMA_URL"
    echo ""
    echo "Make sure Ollama is running:"
    echo "  - Docker: make infra-up"
    echo "  - Local:  ollama serve"
    exit 1
fi
echo "✓ Ollama is running"
echo ""

# Models to pull
MODELS=(
    "llama3.2"           # Main LLM for chat/completion
    "nomic-embed-text"   # Embedding model
)

# Pull each model
for model in "${MODELS[@]}"; do
    echo "Pulling $model..."
    
    # Check if model already exists
    if curl -s "$OLLAMA_URL/api/tags" | grep -q "\"$model\""; then
        echo "✓ $model already pulled"
    else
        # Pull the model
        curl -X POST "$OLLAMA_URL/api/pull" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$model\"}" \
            --no-progress-meter
        echo "✓ $model pulled successfully"
    fi
    echo ""
done

echo "======================================"
echo "All models pulled!"
echo "======================================"
echo ""
echo "Available models:"
curl -s "$OLLAMA_URL/api/tags" | grep -oP '"name":"[^"]+' | sed 's/"name":"/  - /'

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

echo "======================================"
echo "Renai Setup Script"
echo "======================================"
echo ""

# Check for Python 3.11+
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        echo "Error: Python 3.11+ required, found $PYTHON_VERSION"
        exit 1
    fi
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "Error: Python 3 not found"
    exit 1
fi

# Check/Install uv
echo ""
echo "Checking uv package manager..."
if ! command -v uv &> /dev/null; then
    echo "uv not found."
    echo ""
    echo "Please install uv manually using one of these methods:"
    echo "  - pip: pip install uv"
    echo "  - pipx: pipx install uv"
    echo "  - Homebrew: brew install uv"
    echo "  - Official installer: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "For more options, visit: https://github.com/astral-sh/uv#installation"
    exit 1
fi
echo "✓ uv $(uv --version) found"

# Install dependencies
echo ""
echo "Installing dependencies..."
uv sync

# Setup environment file
echo ""
echo "Setting up environment..."
if [ ! -f .env ]; then
    if [ -f deploy/.env.example ]; then
        cp deploy/.env.example .env
        echo "✓ Created .env from template"
    fi
else
    echo "✓ .env already exists"
fi

# Check Docker
echo ""
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    echo "✓ Docker $(docker --version | cut -d' ' -f3 | tr -d ',') found"
else
    echo "⚠ Docker not found - required for infrastructure services"
fi

# Check Docker Compose
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "✓ Docker Compose found"
else
    echo "⚠ Docker Compose not found - required for infrastructure services"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Start infrastructure: make infra-up"
echo "  2. Pull LLM models:      ./scripts/pull-models.sh"
echo "  3. Run services:         make run-all"
echo ""
echo "See docs/getting-started.md for more information."

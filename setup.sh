#!/bin/bash

echo "Setting up Intelligent File Organizer"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is required but not installed"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing Ollama..."
    
    # Install Ollama based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "ERROR: Unsupported OS. Please install Ollama manually from https://ollama.ai"
        exit 1
    fi
fi

# Start Ollama service
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Give Ollama time to start
sleep 5

# Pull the default model
echo "Pulling default AI model (llama3.2:1b)..."
ollama pull llama3.2:1b

echo "Setup complete!"
echo ""
echo "Usage examples:"
echo "  python3 file_organizer.py /path/to/directory"
echo "  python3 file_organizer.py /path/to/directory --dry-run"
echo "  python3 file_organizer.py /path/to/directory --headless"
echo "  python3 file_organizer.py /path/to/directory --extensions .txt,.py,.md"
echo ""
echo "To stop Ollama service: kill $OLLAMA_PID" 
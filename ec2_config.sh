#!/bin/bash

set -e  # Exit if any command fails

echo "Updating package lists..."
sudo apt-get update

echo "Installing software-properties-common to manage repositories..."
sudo apt-get install -y software-properties-common

echo "Ensuring universe repository is enabled..."
sudo add-apt-repository universe
sudo apt-get update

echo "Installing required system packages..."
sudo apt-get install -y python3 python3-pip python3-venv curl

echo "Installing required system packages..."
sudo apt-get install -y python3-pip python3-venv curl

echo "Creating Python virtual environment"
python3 -m venv ~/venv

echo "Activating virtual environment..."
source "~/venv/bin/activate"

echo "Upgrading pip in virtual environment..."
pip install --upgrade pip

echo "Installing Python packages in virtual environment..."
pip install python-dotenv langchain langchain-community langchain-ollama pypdf transformers
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install reportlab

echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Pulling llama3 model via Ollama..."
ollama pull llama3

echo "Running llama3 model via Ollama in the background..."
nohup ollama run llama3 > ollama_llama3.log 2>&1 &

echo "Setup complete."
echo "To activate your virtual environment later, run:"
echo "source venv/bin/activate"

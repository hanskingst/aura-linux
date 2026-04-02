#!/bin/bash
# Run this INSIDE the VM to install dependencies
set -e

echo "=== Aura Linux VM Setup Script ==="
echo "This will install: Ollama, nftables, Python dependencies"

# Update system
sudo apt update

# Install base packages
sudo apt install -y python3 python3-pip nftables curl git

# Install Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Pull the AI model (this will take a few minutes)
echo "Pulling llama3.2:1b model..."
ollama pull llama3.2:1b

# Clone the repo (you'll replace with your actual GitHub URL)
# git clone https://github.com/YOUR_USERNAME/aura-linux.git

echo "Setup complete!"
#!/bin/bash
set -e

echo "=== Aura Linux VM Setup Script ==="
echo "This will install: Ollama, nftables, Python dependencies"

# Update system
sudo apt update

# Install base packages
sudo apt install -y python3 python3-pip nftables curl git

# Install Ollama (SAFE WAY)
echo "Installing Ollama..."

INSTALL_SCRIPT="ollama_install.sh"

# Download with retry + resume + HTTP/1.1
curl --http1.1 -L \
  --retry 5 \
  --retry-delay 5 \
  --continue-at - \
  https://ollama.com/install.sh \
  -o $INSTALL_SCRIPT

# Validate download
if [ ! -s "$INSTALL_SCRIPT" ]; then
  echo "❌ Failed to download Ollama install script"
  exit 1
fi

# Run install script
sh $INSTALL_SCRIPT

# Pull model (retry-safe)
echo "Pulling llama3.2:1b model..."

n=0
until [ $n -ge 5 ]
do
  ollama pull llama3.2:1b && break
  n=$((n+1))
  echo "Retrying model pull ($n/5)..."
  sleep 5
done

if [ $n -eq 5 ]; then
  echo "❌ Failed to pull model after retries"
  exit 1
fi

echo "Setup complete!"
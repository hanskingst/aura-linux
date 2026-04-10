#!/bin/bash
echo "Updating Aura Firewall..."

# Stop firewall
sudo systemctl stop aura-firewall

# Copy updated files
sudo cp src/*.py /usr/local/bin/
sudo cp scripts/aura-cli.py /usr/local/bin/aura
sudo chmod +x /usr/local/bin/aura

# Ensure Ollama is running
if ! systemctl is-active --quiet ollama; then
    sudo systemctl start ollama
    sleep 2
fi

# Start firewall back
sudo systemctl start aura-firewall

echo "Update complete!"
sudo systemctl status aura-firewall --no-pager
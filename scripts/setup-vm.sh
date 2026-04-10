#!/bin/bash
set -e

echo "=========================================="
echo "   Aura Linux - VM Setup Script"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama not found!"
    
    # Check if aria2 is installed, if not install it
    if ! command -v aria2c &> /dev/null; then
        echo "Installing aria2 for faster downloads..."
        sudo apt update
        sudo apt install -y aria2
    fi
    
    echo "Downloading Ollama with aria2..."
    aria2c -x 16 -s 16 -o ollama_install.sh https://ollama.com/install.sh
    
    echo "Installing Ollama..."
    sh ollama_install.sh
    rm ollama_install.sh
    
    echo "✅ Ollama installed successfully"
fi

# Check if model exists
if ! ollama list | grep -q "llama3.2:1b"; then
    echo "⚠️ Model not found. Pulling llama3.2:1b..."
    ollama pull llama3.2:1b
else
    echo "✅ Model already present"
fi

# Copy firewall files
echo "[5/8] Installing firewall files..."
sudo cp src/threat_intel.py /usr/local/bin/
sudo cp src/firewall_daemon.py /usr/local/bin/
sudo chmod +x /usr/local/bin/*.py

# Create data directory
echo "[6/8] Creating data directories..."
sudo mkdir -p /var/lib/aura-firewall/blacklists

# Install systemd services
echo "[7/8] Installing systemd services..."
sudo cp systemd/aura-firewall.service /etc/systemd/system/
sudo cp systemd/aura-threat-update.service /etc/systemd/system/
sudo cp systemd/aura-threat-update.timer /etc/systemd/system/

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable aura-firewall
sudo systemctl start aura-firewall
sudo systemctl enable aura-threat-update.timer
sudo systemctl start aura-threat-update.timer

# Download initial threat feeds
echo "[8/8] Downloading threat feeds..."
sudo python3 /usr/local/bin/threat_intel.py

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="

# Show status
sudo systemctl status aura-firewall --no-pager
echo ""
echo "Threat feed size:"
wc -l /var/lib/aura-firewall/malicious_ips.txt
echo ""
echo "Firewall logs:"
sudo tail -10 /var/log/aura-firewall.log
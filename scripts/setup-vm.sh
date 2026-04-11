#!/bin/bash
set -e

echo "=========================================="
echo "   Aura Linux - VM Setup Script"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama not found! installation started"
    if ! command -v aria2c &> /dev/null; then
        sudo apt update
        sudo apt install -y aria2
    fi
    
    aria2c -x 16 -s 16 -o ollama_install.sh https://ollama.com/install.sh
    sh ollama_install.sh
    rm ollama_install.sh
fi

# Create systemd service for Ollama if not exists
if [ ! -f /etc/systemd/system/ollama.service ]; then
    echo "Creating Ollama systemd service..."
    sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Aura-Linux AI Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable ollama
    sudo systemctl start ollama
    sleep 3
fi

# Check if AI model is pulled
echo "[2/8] Checking AI model..."
if [ -d "$HOME/.ollama/models/blobs" ] && ls ~/.ollama/models/blobs/ | grep -q .; then
    echo "✅ Model already present"
else
    echo "⚠️ Model not found. Pulling llama3.2:1b..."
    ollama pull llama3.2:1b
    echo "model pulled successfully"
fi

# Copy firewall files
echo "[3/8] Installing firewall files..."
sudo cp src/threat_intel.py /usr/local/bin/
sudo cp src/firewall_daemon.py /usr/local/bin/
sudo cp src/ai_decision.py /usr/local/bin/
sudo cp src/ai_explain.py /usr/local/bin/
sudo chmod +x /usr/local/bin/*.py

# Copy CLI tool
echo "[4/8] Installing aura command..."
sudo cp scripts/aura-cli.py /usr/local/bin/aura
sudo chmod +x /usr/local/bin/aura

# Create data directories
echo "[5/8] Creating data directories..."
sudo mkdir -p /var/lib/aura-firewall/blacklists

# Create whitelist
echo "[6/8] Creating whitelist..."
sudo cp src/whitelist.txt /var/lib/aura-firewall/whitelist.txt 2>/dev/null || echo "No whitelist file found, skipping"

# Install systemd services
echo "[7/8] Installing systemd services..."
sudo cp systemd/aura-firewall.service /etc/systemd/system/
sudo cp systemd/aura-threat-update.service /etc/systemd/system/
sudo cp systemd/aura-threat-update.timer /etc/systemd/system/

# Reload and start
sudo systemctl daemon-reload
sudo systemctl enable aura-firewall
sudo systemctl enable aura-threat-update.timer

# Download initial threat feeds
echo "[8/8] Downloading threat feeds..."
sudo python3 /usr/local/bin/threat_intel.py

# Start firewall (after everything is in place)
sudo systemctl start aura-firewall

echo ""
echo "=========================================="
echo "   Setup Complete!"
echo "=========================================="

# Show status
sudo systemctl status aura-firewall --no-pager
echo ""
echo "Ollama service status:"
sudo systemctl status ollama --no-pager | head -3
echo ""
echo "Threat feed size:"
wc -l /var/lib/aura-firewall/malicious_ips.txt 2>/dev/null || echo "Not yet downloaded"
echo ""
echo "Firewall logs:"
sudo tail -10 /var/log/aura-firewall.log 2>/dev/null || echo "No logs yet"
echo ""
echo "Test aura commands:"
echo "  aura health"
echo "  aura explain 8.8.8.8"
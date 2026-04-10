#!/bin/bash
set -e

echo "=========================================="
echo "   Aura Linux - VM Setup Script"
echo "=========================================="

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️ Ollama not found!"
fi

# Start Ollama service if not running
echo "[1/8] Starting Ollama service..."
if ! systemctl is-active --quiet ollama; then
    echo "Starting Ollama service..."
    sudo systemctl start ollama
    # Wait for service to be ready
    sleep 3
fi

# Enable Ollama to start on boot
sudo systemctl enable ollama

# Check if AI model is pulled
echo "[2/8] Checking AI model..."
if ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
    echo "✅ Model already present"
else
    echo "⚠️ Model not found. Pulling llama3.2:1b (this may take a few minutes)..."
    ollama pull llama3.2:1b
    echo "✅ Model pulled successfully"
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
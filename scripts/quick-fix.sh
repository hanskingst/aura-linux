#!/bin/bash
echo "=========================================="
echo "   Aura Linux - Quick Fix"
echo "=========================================="

# Fix firewall service
sudo tee /etc/systemd/system/aura-firewall.service > /dev/null << 'SERVICE'
[Unit]
Description=Aura Linux AI Firewall
After=network-online.target ollama.service
Wants=ollama.service

[Service]
Type=simple
ExecStart=/usr/local/bin/firewall_daemon.py
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
SERVICE

# Start and enable Ollama
sudo systemctl enable ollama
sudo systemctl start ollama

# Download threat feeds
sudo python3 /usr/local/bin/threat_intel.py

# Download AI model
ollama pull llama3.2:1b

# Reload and restart firewall
sudo systemctl daemon-reload
sudo systemctl enable aura-firewall
sudo systemctl start aura-firewall

echo "=========================================="
echo "   Quick Fix Complete!"
echo "=========================================="
echo "Test with: aura health"
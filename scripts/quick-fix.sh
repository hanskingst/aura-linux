#!/bin/bash
echo "=========================================="
echo "   Aura Linux - Quick Fix"
echo "=========================================="

# Restart firewall
echo "[1/3] Restarting firewall service..."
sudo systemctl restart aura-firewall

# Reload threat feeds
echo "[2/3] Reloading threat feeds..."
sudo python3 /usr/local/bin/threat_intel.py

# Show status
echo "[3/3] Current status:"
sudo systemctl status aura-firewall --no-pager

echo ""
echo "If problems persist, run:"
echo "  sudo journalctl -u aura-firewall -n 50"
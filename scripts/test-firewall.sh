#!/bin/bash
echo "=========================================="
echo "   Aura Linux - Firewall Test"
echo "=========================================="

# Test 1: Service status
echo ""
echo "[TEST 1] Checking firewall service..."
if sudo systemctl is-active --quiet aura-firewall; then
    echo "✅ Firewall service is RUNNING"
else
    echo "❌ Firewall service is NOT running"
    sudo systemctl status aura-firewall --no-pager
fi

# Test 2: nftables rules
echo ""
echo "[TEST 2] Checking nftables rules..."
if sudo nft list chain inet aura_filter aura_block 2>/dev/null; then
    echo "✅ nftables chain exists"
else
    echo "⚠️ nftables chain not found (this is normal if no IPs blocked yet)"
fi

# Test 3: Blacklist size
echo ""
echo "[TEST 3] Checking threat feed blacklist..."
BLACKLIST_SIZE=$(wc -l < /var/lib/aura-firewall/malicious_ips.txt 2>/dev/null || echo "0")
if [ "$BLACKLIST_SIZE" -gt 100 ]; then
    echo "✅ Blacklist loaded: $BLACKLIST_SIZE malicious IPs"
else
    echo "⚠️ Blacklist has only $BLACKLIST_SIZE IPs (may need to download)"
fi

# Test 4: Ollama
echo ""
echo "[TEST 4] Checking Ollama..."
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service is RUNNING"
else
    echo "⚠️ Ollama service not running (starting manually)"
    ollama serve &
    sleep 2
fi

# Test 5: AI model
echo ""
echo "[TEST 5] Checking AI model..."
if ollama list | grep -q "llama3.2:1b"; then
    echo "✅ llama3.2:1b model is available"
else
    echo "❌ Model not found - run: ollama pull llama3.2:1b"
fi

# Test 6: Log file
echo ""
echo "[TEST 6] Checking logs..."
if [ -f /var/log/aura-firewall.log ]; then
    echo "✅ Log file exists"
    echo "Last 5 log entries:"
    sudo tail -5 /var/log/aura-firewall.log
else
    echo "❌ Log file not found"
fi

# Test 7: Block a test IP (optional)
echo ""
echo "[TEST 7] Testing block functionality (optional)..."
read -p "Do you want to test blocking an IP? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    TEST_IP="185.130.5.253"
    echo "Testing with known malicious IP: $TEST_IP"
    sudo nft add rule inet aura_filter aura_block ip saddr $TEST_IP drop 2>/dev/null || echo "IP already blocked or chain not ready"
    echo "✅ Block rule added (if it wasn't already)"
    echo "Current blocked IPs:"
    sudo nft list chain inet aura_filter aura_block 2>/dev/null | grep "ip saddr" || echo "No IPs blocked yet"
fi

echo ""
echo "=========================================="
echo "   Test Complete!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  - View logs:        sudo tail -f /var/log/aura-firewall.log"
echo "  - Check service:    sudo systemctl status aura-firewall"
echo "  - See blocked IPs:  sudo nft list chain inet aura_filter aura_block"
echo "  - Test AI:          ollama run llama3.2:1b"
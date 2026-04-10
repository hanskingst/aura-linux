#!/usr/bin/env python3
"""
Aura Linux Firewall Layer 0 + AI Layer
Blocks known malicious IPs from threat feeds.
Uses AI for unknown (gray area) IPs.
"""

import logging
import subprocess
import sys
import time
import os
import ipaddress
from typing import Set

# Import our threat intel module
from threat_intel import load_blacklist

# Import AI decision module
from ai_decision import ask_about_ip

# Configuration
CHECK_INTERVAL_SEC = 5
LOG_FILE = "/var/log/aura-firewall.log"
NFT_TABLE = "aura_filter"
NFT_CHAIN = "aura_block"
WHITELIST_FILE = "/var/lib/aura-firewall/whitelist.txt"

# ----------------------------------------------------------------------
# Logging Setup
# ----------------------------------------------------------------------
def setup_logging():
    logger = logging.getLogger("AuraFirewall")
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ----------------------------------------------------------------------
# Whitelist Functions
# ----------------------------------------------------------------------
def load_whitelist() -> Set[str]:
    """Load known good IPs."""
    if not os.path.exists(WHITELIST_FILE):
        return set()
    with open(WHITELIST_FILE, 'r') as f:
        return {line.strip() for line in f if line.strip() and not line.startswith('#')}

# ----------------------------------------------------------------------
# nftables Functions
# ----------------------------------------------------------------------
def nft_init():
    """Initialize nftables table and chain."""
    subprocess.run(f"nft add table inet {NFT_TABLE} 2>/dev/null", shell=True)
    subprocess.run(
        f"nft add chain inet {NFT_TABLE} {NFT_CHAIN} {{ type filter hook input priority 0\\; policy accept\\; }} 2>/dev/null",
        shell=True
    )
    logger.info("nftables initialized")

def block_ip(ip: str, reason: str = "threat_feed"):
    """Block IP and log reason."""
    try:
        subprocess.run(
            f"nft add rule inet {NFT_TABLE} {NFT_CHAIN} ip saddr {ip} drop",
            shell=True,
            check=True,
            capture_output=True
        )
        logger.info(f"BLOCKED: {ip} (reason: {reason})")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to block {ip}: {e}")
        return False

def is_ip_blocked(ip: str) -> bool:
    """Check if IP already blocked."""
    result = subprocess.run(
        f"nft list chain inet {NFT_TABLE} {NFT_CHAIN} 2>/dev/null | grep -q '{ip} drop'",
        shell=True
    )
    return result.returncode == 0

def load_blocked_ips_from_nft() -> Set[str]:
    """Load currently blocked IPs from nftables."""
    result = subprocess.run(
        f"nft list chain inet {NFT_TABLE} {NFT_CHAIN} 2>/dev/null | grep 'ip saddr' | awk '{{print $4}}'",
        shell=True,
        capture_output=True,
        text=True
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}

# ----------------------------------------------------------------------
# Connection Monitoring
# ----------------------------------------------------------------------
def get_active_remote_ips() -> Set[str]:
    """Get currently connected remote IPs."""
    result = subprocess.run(["ss", "-tn"], capture_output=True, text=True)
    ips = set()
    
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 5:
            continue
        remote = parts[4]
        ip = remote.split(":")[0]
        
        # Skip private IPs
        if ip.startswith(('127.', '10.', '192.168.', '172.')):
            continue
        
        # Validate IPv4
        if ip.count('.') == 3:
            try:
                ipaddress.ip_address(ip)
                ips.add(ip)
            except ValueError:
                continue
            except Exception as e:
                logger.warning(f"Unexpected error validating IP {ip}: {e}")
                continue
    
    return ips

# ----------------------------------------------------------------------
# Blacklist Sync
# ----------------------------------------------------------------------
def sync_blacklist():
    """Load latest blacklist and ensure all IPs are blocked."""
    malicious_ips = load_blacklist()
    currently_blocked = load_blocked_ips_from_nft()
    
    for ip in malicious_ips:
        if ip not in currently_blocked:
            block_ip(ip, "threat_feed")
    
    logger.info(f"Blacklist sync complete: {len(malicious_ips)} IPs in blacklist, {len(currently_blocked)} currently blocked")
    return malicious_ips

# ----------------------------------------------------------------------
# Main Monitoring Loop
# ----------------------------------------------------------------------
def monitor_connections():
    """Main monitoring loop with AI for gray-area IPs."""
    nft_init()
    
    # Initial sync
    malicious_ips = sync_blacklist()
    whitelist = load_whitelist()
    
    logger.info("=" * 50)
    logger.info("Aura Firewall Started (AI Enhanced Mode)")
    logger.info(f"Loaded {len(malicious_ips)} malicious IPs from blacklist")
    logger.info(f"Loaded {len(whitelist)} IPs in whitelist")
    logger.info(f"Monitoring every {CHECK_INTERVAL_SEC} seconds")
    logger.info("=" * 50)
    
    processed_ips = set()
    
    try:
        while True:
            current_ips = get_active_remote_ips()
            new_ips = current_ips - processed_ips
            
            for ip in new_ips:
                # Skip if already blocked
                if is_ip_blocked(ip):
                    logger.info(f"{ip} already blocked")
                    processed_ips.add(ip)
                    continue
                
                # Layer 1: Check blacklist
                if ip in malicious_ips:
                    logger.warning(f"⚠️ MALICIOUS IP detected: {ip} - blocking")
                    block_ip(ip, "threat_feed_active")
                
                # Layer 2: Check whitelist
                elif ip in whitelist:
                    logger.info(f"✓ IP {ip} is whitelisted - allowing")
                
                # Layer 3: Gray area - Ask AI
                else:
                    logger.info(f"🤔 Unknown IP {ip} - asking AI...")
                    is_malicious, explanation, confidence = ask_about_ip(ip)
                    
                    if is_malicious:
                        logger.warning(f"🤖 AI says {ip} is MALICIOUS (confidence: {confidence})")
                        logger.warning(f"   Reason: {explanation}")
                        block_ip(ip, f"ai_decision_{confidence}")
                    else:
                        logger.info(f"🤖 AI says {ip} is safe (confidence: {confidence})")
                        logger.info(f"   Reason: {explanation}")
                
                processed_ips.add(ip)
            
            # Periodically reload blacklist and whitelist
            if int(time.time()) % 300 < CHECK_INTERVAL_SEC:
                malicious_ips = sync_blacklist()
                whitelist = load_whitelist()
            
            time.sleep(CHECK_INTERVAL_SEC)
    
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)

# ----------------------------------------------------------------------
# Entry Point
# ----------------------------------------------------------------------
def main():
    monitor_connections()

if __name__ == "__main__":
    main()
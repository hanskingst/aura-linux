#!/usr/bin/env python3
"""
Threat Intelligence Module - Downloads and manages malicious IP lists
All data stays LOCAL. No cloud APIs called during blocking.
"""

import logging
import os
from typing import Set
import urllib.request

# Configure paths
BLACKLIST_DIR = "/var/lib/aura-firewall/blacklists"
BLACKLIST_FILE = "/var/lib/aura-firewall/malicious_ips.txt"
LOG_FILE = "/var/log/aura-threat-intel.log"

# Free, public threat feeds (no API key needed)
THREAT_FEEDS = {
    "abuseipdb_100": "https://raw.githubusercontent.com/borestad/blocklist-abuseipdb/main/abuseipdb-s100-30d.ipv4",
    "firehol_level1": "https://iplists.firehol.org/files/firehol_level1.netset",
    "ci_army": "https://cinsscore.com/list/ci-badguys.txt",
}

def setup_logging():
    logger = logging.getLogger("ThreatIntel")
    logger.setLevel(logging.INFO)
    os.makedirs(BLACKLIST_DIR, exist_ok=True)
    
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger

logger = setup_logging()

def download_feeds() -> Set[str]:
    """Download all threat feeds and return set of malicious IPs."""
    all_ips = set()
    
    for name, url in THREAT_FEEDS.items():
        try:
            logger.info(f"Downloading {name} from {url}")
            with urllib.request.urlopen(url, timeout=30) as response:
                content = response.read().decode('utf-8')
                
                # Parse IPs (each line is either an IP or CIDR range)
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Simple IP validation (we'll expand CIDR later if needed)
                    if line.count('.') == 3 and all(part.isdigit() for part in line.split('.')):
                        all_ips.add(line)
                    # Skip CIDR ranges for now (we'll handle separately)
            
            logger.info(f"  → Added {len([ip for ip in all_ips if ip])} IPs from {name}")
        except Exception as e:
            logger.error(f"Failed to download {name}: {e}")
    
    return all_ips

def save_blacklist(ips: Set[str]):
    """Save IPs to file for fast loading."""
    os.makedirs(BLACKLIST_DIR, exist_ok=True)
    with open(BLACKLIST_FILE, 'w') as f:
        for ip in sorted(ips):
            f.write(f"{ip}\n")
    logger.info(f"Saved {len(ips)} malicious IPs to {BLACKLIST_FILE}")

def load_blacklist() -> Set[str]:
    """Load IPs from file (fast startup)."""
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    
    with open(BLACKLIST_FILE, 'r') as f:
        return {line.strip() for line in f if line.strip()}

def update_threat_intel():
    """Main function to update threat intelligence."""
    logger.info("Starting threat intelligence update...")
    ips = download_feeds()
    save_blacklist(ips)
    logger.info("Update complete")
    return ips

if __name__ == "__main__":
    # Run this daily via cron or systemd timer
    update_threat_intel()
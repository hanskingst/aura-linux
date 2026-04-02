#!/usr/bin/env python3
"""
Aura Linux AI Firewall Daemon
This will monitor connections and ask Ollama whether to block IPs.
"""

import logging
import subprocess
import time
import requests
from typing import Set

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"
CHECK_INTERVAL_SEC = 10
LOG_FILE = "/var/log/aura-firewall.log"
NFT_TABLE = "aura_filter"
NFT_CHAIN = "aura_block"

def main():
    """Main entry point - will implement monitoring loop"""
    print("Aura Firewall starting... (placeholder)")
    # We'll fill this in step by step

if __name__ == "__main__":
    main()
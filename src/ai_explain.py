#!/usr/bin/env python3
"""
AI Explanation Module For user questions about blocks and health
"""

import requests
import logging
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"
LOG_FILE = "/var/log/aura-firewall.log"

logger = logging.getLogger("AuraFirewall.Explain")

def get_logs_for_ip(ip: str, lines: int = 20) -> str:
    """Extract log entries for a specific IP."""
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()
        
        relevant = [line for line in logs if ip in line]
        return ''.join(relevant[-lines:]) if relevant else "No logs found for this IP"
    except Exception as e:
        return f"Error reading logs: {e}"

def explain_ip(ip: str) -> str:
    """Generate AI explanation for why an IP was blocked."""
    
    # Get relevant logs
    logs = get_logs_for_ip(ip)
    
    prompt = f"""You are Aura Firewall's explanation engine. A user asked: "Why was {ip} blocked?"

Here are the relevant logs:
{logs}

Based on these logs, explain in 2-3 sentences:
1. Why this IP was blocked
2. What action was taken
3. What the user should do (if anything)

Be helpful and conversational, but technical."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=500)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Unable to generate explanation")
    except Exception as e:
        return f"Error getting explanation: {e}"

def get_firewall_health() -> str:
    """Generate AI report on firewall health."""
    
    # Collect system state
    import subprocess
    
    # Get service status
    service_result = subprocess.run(
        ["systemctl", "is-active", "aura-firewall"],
        capture_output=True, text=True
    )
    service_status = service_result.stdout.strip()
    
    # Get nftables rule count
    nft_result = subprocess.run(
        ["nft", "list", "chain", "inet", "aura_filter", "aura_block"],
        capture_output=True, text=True
    )
    rule_count = nft_result.stdout.count("ip saddr")
    
    # Get blacklist size
    blacklist_path = Path("/var/lib/aura-firewall/malicious_ips.txt")
    blacklist_size = len(blacklist_path.read_text().splitlines()) if blacklist_path.exists() else 0
    
    # Get last log time
    log_time = "unknown"
    try:
         with open(LOG_FILE, 'r') as f:
          lines = f.readlines()
         if lines:
            last_line = lines[-1]
            log_time = last_line.split(" - ")[0] if last_line else "unknown"
    except FileNotFoundError:
     log_time = "Log file not found yet"
    except Exception as e:
     log_time = f"Error reading log: {e}"
    
    prompt = f"""You are Aura Firewall's health reporter. Generate a concise health report:

Firewall Status: {service_status}
Active Block Rules: {rule_count}
Threat Feed Size: {blacklist_size} malicious IPs
Last Log Entry: {log_time}

Provide a 3-sentence summary of:
- Overall health (good/warning/critical)
- Key metrics
- Any recommendations

Be professional but friendly."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.5}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=500)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Unable to generate health report")
    except Exception as e:
        return f"Error getting health report: {e}"
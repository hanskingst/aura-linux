#!/usr/bin/env python3
"""
AI Decision Module - For unknown IPs only
Returns: (is_malicious, explanation, confidence)
"""

import json
import requests
import logging
from typing import Tuple

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

logger = logging.getLogger("AuraFirewall.AI")

def ask_about_ip(ip: str, context: dict = None) -> Tuple[bool, str, float]:
    """
    Ask AI about an IP address.
    Returns: (is_malicious, explanation, confidence)
    """
    if context is None:
        context = {}
    
    prompt = f"""You are a network security expert. Analyze this IP address:

IP: {ip}
Context: {context.get('notes', 'No additional context')}

Answer in EXACTLY this JSON format:
{{
    "malicious": true/false,
    "explanation": "one sentence reason",
    "confidence": 0.0-1.0
}}

Only respond with valid JSON. No other text."""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=500)
        response.raise_for_status()
        result = response.json()
        
        # Parse JSON response
        ai_output = json.loads(result.get("response", "{}"))
        
        malicious = ai_output.get("malicious", False)
        explanation = ai_output.get("explanation", "No explanation provided")
        confidence = ai_output.get("confidence", 0.5)
        
        logger.info(f"AI decision for {ip}: malicious={malicious}, confidence={confidence}")
        return malicious, explanation, confidence
        
    except Exception as e:
        logger.error(f"AI query failed for {ip}: {e}")
        return False, f"AI error: {e}", 0.0
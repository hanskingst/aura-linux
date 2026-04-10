#!/usr/bin/env python3
"""
Aura Firewall CLI User commands
Usage:
    aura explain 1.2.3.4
    aura health
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  aura explain <IP>     - Explain why an IP was blocked")
        print("  aura health           - Get firewall health report")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "explain":
        if len(sys.argv) < 3:
            print("Error: Please provide an IP address")
            print("Usage: aura explain 1.2.3.4")
            sys.exit(1)
        ip = sys.argv[2]
        
        from ai_explain import explain_ip
        print(f"\n🔍 Analyzing {ip}...\n")
        print(explain_ip(ip))
        
    elif command == "health":
        from ai_explain import get_firewall_health
        print("\n🏥 Aura Firewall Health Report\n")
        print(get_firewall_health())
        
    else:
        print(f"Unknown command: {command}")
        print("Available: explain, health")

if __name__ == "__main__":
    main()
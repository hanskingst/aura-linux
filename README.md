# Aura Linux - AI-Native OS with Intelligent Firewall

An Ubuntu-based Linux distribution with an AI-powered firewall using local LLM inference.

## Project Structure

- `src/` - Python source code for the firewall daemon
- `systemd/` - Service files for auto-start
- `scripts/` - Setup and utility scripts
- `docs/` - Documentation

## Quick Start

1. Run `scripts/setup-vm.sh` inside a Ubuntu 22.04 VM
2. The firewall daemon will automatically start
3. Check logs at `/var/log/aura-firewall.log`

## Architecture

The firewall monitors network connections and queries a local Ollama instance
(llama3.2:1b) to determine if an IP address is malicious. If the AI responds
with "YES", the IP is blocked using nftables.

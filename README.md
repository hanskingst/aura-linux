# Aura Linux - AI-Native OS with Intelligent Firewall

An Ubuntu-based Linux distribution with an AI-powered firewall using local LLM inference.

## Project Structure

- `src/` - Python source code for the firewall daemon
- `systemd/` - Service files for auto-start
- `scripts/` - Setup and utility scripts
- `docs/` - Documentation

## Quick Start for Aura Firewall test on an existing Ubuntu system

1. Run `scripts/setup-vm.sh` inside a Ubuntu 22.04 VM, this is when you want to test only the Aura Firewall on a linux system without installing the bundled custom distro which will be the same with the difference that you have to install packages from the internet.
2. The firewall daemon will automatically start
3. Check logs at `/var/log/aura-firewall.log`

## Quick Start when you use the custom linux distro

1. After installing the distro on a machine or virtualbox,
2. Since for now during the iso building there were mistakes in some system file you will have to install git on your vm using `sudo apt update` then `sudo apt install git`
3. After installing git you have to pull the repo from github using `git pull github.com/hanskingst/aura-linux` if any issue arises after pulling run `git fetch origin/main`.
4. After pulling the repo locally, navigate to that repo using `cd your/path/to/repo` (replace that with your actual path), then run `./scripts/quick-fix.sh`.
5. After doing that wait for the script to run and it will take time depending on the capacity of your machine then after that you will be good to go.

## Architecture

This is the architectural diagram of Aura linux system.

┌─────────────────────────────────────────────────────────────────────────────┐
│ AURA LINUX SYSTEM │
├─────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ USER SPACE │ │
│ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │ │
│ │ │ aura health │ │ aura explain │ │ aura-cli.py │ │ │
│ │ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │ │
│ │ │ │ │ │ │
│ │ └─────────────────┼─────────────────┘ │ │
│ │ │ │ │
│ │ ┌────────────────────────┼────────────────────────────────────┐ │ │
│ │ │ AI LAYER │ │ │
│ │ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │ │ │
│ │ │ │ ai_decision │ │ ai_explain │ │ threat_intel │ │ │ │
│ │ │ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ │ │ │
│ │ └─────────┼─────────────────┼─────────────────┼────────────────┘ │ │
│ │ │ │ │ │ │
│ │ ┌─────────┼─────────────────┼─────────────────┼────────────────┐ │ │
│ │ │ │ OLLAMA (Local LLM) │ │ │ │
│ │ │ │ llama3.2:1b │ │ │ │
│ │ └─────────┼─────────────────┼─────────────────┼────────────────┘ │ │
│ │ │ │ │ │ │
│ │ ┌─────────┼─────────────────┼─────────────────┼────────────────┐ │ │
│ │ │ │ FIREWALL DAEMON │ │ │ │
│ │ │ │ (firewall_daemon.py) │ │ │ │
│ │ │ └─────────────────┴─────────────────┘ │ │ │
│ │ │ │ │ │ │
│ │ │ ┌──────┴──────┐ │ │ │
│ │ │ │ nftables │ │ │ │
│ │ │ │ (netlink) │ │ │ │
│ │ └───────────────────┼──────┬──────┼─────────────────────────────┘ │ │
│ └───────────────────────┼──────┼──────┼─────────────────────────────────┘ │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ ┌──────────────────────────────────────────────────────────────────────┐ │
│ │ KERNEL SPACE │ │
│ │ ┌────────────────────────────────────────────────────────────────┐ │ │
│ │ │ NETFILTER │ │ │
│ │ │ ┌──────────────────────────────────────────────────────────┐ │ │ │
│ │ │ │ nftables Rules: drop from {malicious_ips} │ │ │ │
│ │ │ └──────────────────────────────────────────────────────────┘ │ │ │
│ │ │ │ │ │ │
│ │ │ ┌──────┴──────┐ │ │ │
│ │ │ │ DROP/ALLOW │ │ │ │
│ │ │ └─────────────┘ │ │ │
│ │ └────────────────────────────────────────────────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────────────────┘ │
│ │ │
│ ▼ │
│ INCOMING/OUTGOING │
│ NETWORK PACKETS │
└─────────────────────────────────────────────────────────────────────────────┘

This is the architecture of the whole system weather you installed the custom ubuntu iso with packages preinstalled or you install them on any ubuntu system.

This system works in the user space of the linux architecture, this system has these layers in the user space.

### Firewall Daemon

This is the layer that monitors the network every 5s, it checks incoming an outgoing IPs against the list of malicious IPs from the `malicious_ips.txt` file and decides wether to block an IP or not if found or not found. How it blocks the IPs is by telling the nftables to drop or allow a particular IP then that nftable will talk to the kernel and the kernel will do that, and after blocking this layer uses nftables rules to persist recent block IPs in the list of malicious IPs.

### Threat Intel layer

This layer is responsible to download the list of malicious IPs from reliable sources like AbuseIPDB,FireHOL etc..., and saving them in the `malicious_ips.txt` file to be used by the firewall daemon. This layer updates the list daily meaning after every 24 hours.

### AI Decision layer

This layer provides the rules for unknown IP addresses, by giving them to the local SLM for analyses, so this layer will then decide if that IP is malicious or not and whatever the decision, the decisioin is then passed to the firewall daemon layer for enforcement.

### AI Explanation layer

This layer analyzes the firewall's analyses on a particular IP (IP passed by the user from the terminal using `aura explain <pass IP>`) and let the local AI interprete or explain it.

### Aura CLI

This layer provides the CLI interface for users to run the health command which will have the local AI give the report of the general health of the firewall through `aura health` command, and the explain command through `aura explain <pass IP>`. These are the only two commands that aura-firewall understands.

### Local SML (llama3.2:1b model) through ollama.

This layer is the AI brain, it provides the system with the AI model that will be used by the firewall.

### Systemd scripts

These scripts are what create the rules for all the firewall code to run as OS lavel background jobs, handling processes like making the Firewall run automatically on boot, run continously. This is what makes the system work at the level of the user space in the kernel architecture.

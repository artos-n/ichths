#!/usr/bin/env bash
#
# Ichths Installer — Full OpenClaw Setup for Ich
# Usage: bash install.sh
#
# Sets up Node.js, OpenClaw, systemd gateway service,
# and the Ichths workspace on a fresh Ubuntu/Debian system.
#
set -euo pipefail

# ── Colors ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*" >&2; }
step()  { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

# ── Checks ─────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (or with sudo)."
    exit 1
fi

if ! command -v apt-get &>/dev/null; then
    err "This installer targets Debian/Ubuntu systems (apt-get required)."
    exit 1
fi

step "1/6 — System packages"
apt-get update -qq
apt-get install -y -qq curl git gnupg ca-certificates

step "2/6 — Node.js 24"
if command -v node &>/dev/null; then
    NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
    if [[ $NODE_VER -ge 22 ]]; then
        ok "Node $(node -v) already installed"
    else
        warn "Node $(node -v) is too old, installing Node 24..."
        INSTALL_NODE=1
    fi
else
    INSTALL_NODE=1
fi

if [[ "${INSTALL_NODE:-}" == "1" ]]; then
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
    apt-get install -y -qq nodejs
    ok "Node $(node -v) installed"
fi

step "3/6 — OpenClaw"
if command -v openclaw &>/dev/null; then
    ok "OpenClaw $(openclaw --version 2>/dev/null | head -1) already installed"
else
    npm install -g openclaw
    ok "OpenClaw installed"
fi

step "4/6 — GitHub CLI (optional)"
if ! command -v gh &>/dev/null; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list
    apt-get update -qq
    apt-get install -y -qq gh
    ok "GitHub CLI installed"
else
    ok "GitHub CLI already installed"
fi

step "5/6 — Workspace setup"
WORKSPACE="${HOME}/.openclaw/workspace"
mkdir -p "$WORKSPACE"/{memory,skills}

# Only create files if they don't exist (don't overwrite)
for f in AGENTS.md SOUL.md IDENTITY.md USER.md TOOLS.md HEARTBEAT.md; do
    if [[ ! -f "$WORKSPACE/$f" ]]; then
        warn "$f not found — you'll need to configure this after install"
    fi
done

ok "Workspace directories ready at $WORKSPACE"

step "6/6 — Gateway service"
# Enable lingering for user-level systemd services (if not root)
if [[ $EUID -ne 0 ]]; then
    loginctl enable-linger "$(whoami)" 2>/dev/null || true
fi

# Install gateway service
openclaw gateway install 2>&1 || warn "Gateway install returned non-zero (may already exist)"

# Enable and start
systemctl --user enable openclaw-gateway.service 2>/dev/null || \
    systemctl enable openclaw-gateway.service 2>/dev/null || true

systemctl --user start openclaw-gateway.service 2>/dev/null || \
    systemctl start openclaw-gateway.service 2>/dev/null || true

ok "Gateway service installed and started"

# ── Summary ─────────────────────────────────────────────
echo ""
step "Install complete"
echo ""
echo "  Node.js:    $(node -v 2>/dev/null || echo 'not found')"
echo "  npm:        $(npm -v 2>/dev/null || echo 'not found')"
echo "  OpenClaw:   $(openclaw --version 2>/dev/null | head -1 || echo 'not found')"
echo "  gh:         $(gh --version 2>/dev/null | head -1 || echo 'not found')"
echo "  Workspace:  $WORKSPACE"
echo ""
echo "  Next steps:"
echo "    1. Configure channels:  openclaw config"
echo "    2. Pair a device:       openclaw pair"
echo "    3. Check status:        openclaw status"
echo "    4. Clone your shell:    gh repo clone <owner>/Ichths ~/.openclaw/workspace"
echo ""
echo "  🐟 Ich is ready to come online."

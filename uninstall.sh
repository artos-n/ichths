#!/usr/bin/env bash
#
# Ichths Uninstaller — Remove OpenClaw and Ich
# Usage: bash uninstall.sh
#
# Removes OpenClaw, the gateway service, and optionally the workspace.
# Does NOT remove Node.js (too many things depend on it).
#
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERR]${NC}   $*" >&2; }

echo ""
echo "  This will remove OpenClaw and the Ichths workspace."
echo ""
read -rp "  Remove workspace data too? [y/N] " REMOVE_DATA

# Stop and remove service
info "Stopping gateway service..."
systemctl --user stop openclaw-gateway.service 2>/dev/null || true
systemctl --user disable openclaw-gateway.service 2>/dev/null || true
systemctl stop openclaw-gateway.service 2>/dev/null || true
systemctl disable openclaw-gateway.service 2>/dev/null || true

# Remove OpenClaw
info "Removing OpenClaw..."
npm uninstall -g openclaw 2>/dev/null || true

# Remove workspace if requested
if [[ "${REMOVE_DATA,,}" == "y" ]]; then
    warn "Removing workspace data at ~/.openclaw"
    rm -rf ~/.openclaw
    info "Workspace removed"
else
    info "Workspace preserved at ~/.openclaw"
fi

echo ""
info "Uninstall complete."
echo "  Node.js was NOT removed (uninstall manually if needed)."
echo ""

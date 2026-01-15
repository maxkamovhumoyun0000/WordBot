#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_to_server.sh <remote_user@host> <remote_path>
# Example: ./deploy_to_server.sh ubuntu@server /home/ubuntu/bot

REMOTE=${1:-ubuntu@server}
REMOTE_PATH=${2:-/home/ubuntu/bot}

# Files/dirs to exclude from deployment
EXCLUDES=(--exclude 'venv' --exclude '__pycache__' --exclude '.git' --exclude '*.pyc' \
  --exclude 'TRIGONOMETRY_INTEGRATION.md' --exclude 'test_*' --exclude 'tests')

LOCAL_DIR=$(pwd)

echo "Deploying ${LOCAL_DIR} -> ${REMOTE}:${REMOTE_PATH}"

rsync -az --delete "${EXCLUDES[@]}" ./ "${REMOTE}:${REMOTE_PATH}/"

echo "\nDeploy finished. Next steps on the server (SSH):"
echo "  ssh ${REMOTE}"
echo "  cd ${REMOTE_PATH}"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  # Create systemd unit from deploy/wordl.service (or use the example)"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable --now wordl.service"
echo "\nIf you need me to create or adapt the systemd unit, tell me and I will add it to the repo."

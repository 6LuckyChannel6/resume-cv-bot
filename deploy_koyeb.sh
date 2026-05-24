#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${KOYEB_APP_NAME:-resume-cv-bot}"
SERVICE_NAME="${KOYEB_SERVICE_NAME:-web}"
REGION="${KOYEB_REGION:-fra}"
PORT="${PORT:-8000}"
KOYEB_BIN="${KOYEB_BIN:-$HOME/.koyeb/bin/koyeb}"
DEPLOY_DIR="$(mktemp -d)"
trap 'rm -rf "$DEPLOY_DIR"' EXIT

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${KOYEB_TOKEN:?Set KOYEB_TOKEN to your Koyeb API token}"
: "${BOT_TOKEN:?Set BOT_TOKEN in .env or the environment}"

WEBHOOK_SECRET="${WEBHOOK_SECRET:-$(python3 - <<'PY'
import hashlib
import os
print(hashlib.sha256(os.environ["BOT_TOKEN"].encode()).hexdigest()[:32])
PY
)}"

cp Dockerfile requirements.txt bot.py cv_generator.py translator.py "$DEPLOY_DIR"/

"$KOYEB_BIN" deploy "$DEPLOY_DIR" "$APP_NAME/$SERVICE_NAME" \
  --archive-builder docker \
  --archive-docker-dockerfile Dockerfile \
  --type web \
  --instance-type free \
  --regions "$REGION" \
  --scale 1 \
  --ports "$PORT:http" \
  --routes "/:$PORT" \
  --checks "$PORT:http:/health" \
  --env "BOT_TOKEN=$BOT_TOKEN" \
  --env "WEBHOOK_SECRET=$WEBHOOK_SECRET" \
  --env "PYTHONUNBUFFERED=1" \
  --wait \
  --token "$KOYEB_TOKEN"

echo
echo "Deployment requested for $APP_NAME/$SERVICE_NAME."
echo "After Koyeb becomes healthy, stop the local LaunchAgent to avoid polling/webhook conflicts:"
echo "launchctl bootout \"gui/\$(id -u)\" \"\$HOME/Library/LaunchAgents/com.lucky.cvbot.plist\""

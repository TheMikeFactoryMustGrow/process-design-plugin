#!/usr/bin/env bash
# Build process-design.plugin from the source tree.
#
# Output: dist/process-design.plugin — zip archive that installs via:
#   - Cowork plugin manager: drag the .plugin file onto it
#   - Direct extraction:     unzip into _claude_config/<name>/
#
# Claude Code installs from the surrounding marketplace via the
# `.claude-plugin/marketplace.json` at the repo root, not from this artifact.

set -euo pipefail

cd "$(dirname "$0")"

PLUGIN_SRC=plugins/process-design

[ -f "$PLUGIN_SRC/.claude-plugin/plugin.json" ] || {
  echo "ERROR: missing $PLUGIN_SRC/.claude-plugin/plugin.json" >&2
  exit 1
}

mkdir -p dist
rm -f dist/process-design.plugin

# Stage in /tmp to avoid permission/ordering issues
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

# Zip the plugin contents so the manifest sits at the zip ROOT
# (.claude-plugin/plugin.json + skills/ at top level inside the zip).
cp -R "$PLUGIN_SRC/." "$STAGE/"

cd "$STAGE"
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find . -name '.DS_Store' -delete 2>/dev/null || true
zip -qr /tmp/process-design.plugin . -x "*.DS_Store" "*__pycache__*"
mv /tmp/process-design.plugin "$OLDPWD/dist/process-design.plugin"

cd "$OLDPWD"
echo "Built: dist/process-design.plugin"
unzip -l dist/process-design.plugin | tail -10

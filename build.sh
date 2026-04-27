#!/usr/bin/env bash
# Build process-design.plugin from the source tree.
# Output: dist/process-design.plugin (zip archive Cowork installs)

set -euo pipefail

cd "$(dirname "$0")"

mkdir -p dist
rm -f dist/process-design.plugin

# Stage in /tmp to avoid permission/ordering issues
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

cp -R .claude-plugin "$STAGE/"
mkdir -p "$STAGE/skills"
for skill in process-design qa-agents dmaic dmaic-define dmaic-measure dmaic-analyze dmaic-improve dmaic-control; do
  cp -R "skills/$skill" "$STAGE/skills/"
done

cd "$STAGE"
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find . -name '.DS_Store' -delete 2>/dev/null || true
zip -qr /tmp/process-design.plugin . -x "*.DS_Store" "*__pycache__*"
mv /tmp/process-design.plugin "$OLDPWD/dist/process-design.plugin"

cd "$OLDPWD"
echo "Built: dist/process-design.plugin"
unzip -l dist/process-design.plugin | tail -20

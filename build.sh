#!/usr/bin/env bash
# Build process-design.plugin from the source tree + Grok skill packages.
#
# Outputs:
#   dist/process-design.plugin  — Claude Cowork drag-and-drop zip
#   dist/grok/*.skill           — Grok Skills / Agent Skills packages
#   dist/grok/process-design-skills.zip
#
# Claude Code installs from the surrounding marketplace via the
# `.claude-plugin/marketplace.json` at the repo root, not from the .plugin artifact.

set -euo pipefail

cd "$(dirname "$0")"

PLUGIN_SRC=plugins/process-design

[ -f "$PLUGIN_SRC/.claude-plugin/plugin.json" ] || {
  echo "ERROR: missing $PLUGIN_SRC/.claude-plugin/plugin.json" >&2
  exit 1
}

command -v python3 >/dev/null 2>&1 || {
  echo "ERROR: python3 required" >&2
  exit 1
}

mkdir -p dist
rm -f dist/process-design.plugin

# Stage + zip via Python (no system `zip` binary required)
python3 - <<'PY'
import shutil
import zipfile
from pathlib import Path

root = Path(".").resolve()
src = root / "plugins" / "process-design"
out = root / "dist" / "process-design.plugin"
stage = root / "dist" / "_plugin_stage"
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)

# copy tree
for path in src.rglob("*"):
    rel = path.relative_to(src)
    # skip caches / evals / junk
    parts = set(rel.parts)
    if "__pycache__" in parts or ".DS_Store" in parts:
        continue
    if "evals" in rel.parts:
        continue
    dest = stage / rel
    if path.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for path in stage.rglob("*"):
        if path.is_file():
            zf.write(path, arcname=str(path.relative_to(stage)).replace("\\", "/"))

shutil.rmtree(stage)
print(f"Built: {out} ({out.stat().st_size} bytes)")
with zipfile.ZipFile(out) as zf:
    names = zf.namelist()
print(f"  entries: {len(names)}")
for n in names[-8:]:
    print(f"  {n}")
PY

echo ""
echo "Packaging Grok skills..."
python3 scripts/package_for_grok.py

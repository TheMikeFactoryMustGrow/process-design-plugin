#!/usr/bin/env python3
"""
Build Grok-ready skill packages from plugins/process-design/skills/.

Outputs:
  dist/grok/<skill>.skill          — one Agent Skills package per skill
  dist/grok/process-design-skills.zip — all skills in one zip (for bulk share)
  dist/grok/MANIFEST.md            — install map for humans

Does not modify Claude marketplace layout or plugins/process-design/skills/ source.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "plugins" / "process-design" / "skills"
RUNTIME_MD = ROOT / "plugins" / "process-design" / "shared" / "agent-runtimes.md"
OUT_DIR = ROOT / "dist" / "grok"
BUNDLE = OUT_DIR / "process-design-skills.zip"

sys.path.insert(0, str(ROOT / "scripts"))
from package_skill import package_skill  # noqa: E402


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills dir missing: {SKILLS_DIR}", file=sys.stderr)
        return 1

    if OUT_DIR.exists():
        for p in OUT_DIR.glob("*.skill"):
            p.unlink()
        if BUNDLE.exists():
            BUNDLE.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and (p / "SKILL.md").exists())
    if not skill_dirs:
        print("ERROR: no skills found", file=sys.stderr)
        return 1

    built: list[Path] = []
    failed: list[str] = []
    for skill_dir in skill_dirs:
        result = package_skill(skill_dir, OUT_DIR, RUNTIME_MD if RUNTIME_MD.exists() else None)
        if result:
            built.append(result)
        else:
            failed.append(skill_dir.name)

    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1

    # Bulk zip: each .skill is already a zip; also ship an exploded skills/ tree
    # so recipients can `cp -R skills/* ~/.grok/skills/` in one step.
    stage = OUT_DIR / "_stage_skills"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    for skill_dir in skill_dirs:
        dest = stage / skill_dir.name
        shutil.copytree(
            skill_dir,
            dest,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "evals"),
        )
        # Ensure runtime adapter present in exploded tree
        if RUNTIME_MD.exists():
            refs = dest / "references"
            refs.mkdir(exist_ok=True)
            target = refs / "agent-runtimes.md"
            if not target.exists():
                shutil.copy2(RUNTIME_MD, target)

    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as zf:
        # Individual .skill packages
        for skill_file in built:
            zf.write(skill_file, arcname=f"skills-packages/{skill_file.name}")
        # Exploded tree for Grok Build / manual copy
        for file_path in stage.rglob("*"):
            if file_path.is_file():
                arc = Path("skills") / file_path.relative_to(stage)
                zf.write(file_path, arcname=str(arc).replace("\\", "/"))
        # Install docs
        install = (ROOT / "docs" / "INSTALL-GROK.md")
        if install.exists():
            zf.write(install, arcname="INSTALL-GROK.md")
        if RUNTIME_MD.exists():
            zf.write(RUNTIME_MD, arcname="agent-runtimes.md")

    shutil.rmtree(stage)

    # MANIFEST
    lines = [
        "# Grok skill packages",
        "",
        f"Built: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Skills: {len(built)}",
        "",
        "| Package | Size |",
        "| --- | ---: |",
    ]
    for p in built:
        lines.append(f"| `{p.name}` | {p.stat().st_size:,} |")
    lines += [
        "",
        f"Bundle: `{BUNDLE.name}` ({BUNDLE.stat().st_size:,} bytes)",
        "",
        "See `docs/INSTALL-GROK.md` for install steps (Grok Skills + Grok Build).",
        "Claude Code / Cowork install path is unchanged — see root README.",
        "",
    ]
    (OUT_DIR / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ Wrote {len(built)} packages + {BUNDLE.name}")
    print((OUT_DIR / "MANIFEST.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

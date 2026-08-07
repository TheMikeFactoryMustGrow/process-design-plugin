#!/usr/bin/env python3
"""
Package one skill folder into a distributable .skill file (zip).

Adapted from Anthropic skill-creator packaging conventions for this repo.
Validates frontmatter lightly (portable across Claude + Grok) and optionally
injects shared/agent-runtimes.md into the package as references/agent-runtimes.md.

Usage:
  python3 scripts/package_skill.py plugins/process-design/skills/process-design dist/grok
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
import zipfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
ROOT_EXCLUDE_DIRS = {"evals"}
EXCLUDE_GLOBS = {"*.pyc", ".DS_Store"}
ALLOWED_FRONTMATTER = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
    # retained in source for humans; not required by Agent Skills core
    "version",
}


def should_exclude(rel: Path) -> bool:
    parts = rel.parts
    if any(p in EXCLUDE_DIRS for p in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel.name
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def validate_skill(skill_path: Path) -> tuple[bool, str, dict]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found", {}

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found", {}

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format", {}

    if yaml is None:
        # Minimal parse without PyYAML: only require name/description lines
        fm_text = match.group(1)
        name_m = re.search(r"^name:\s*(.+)$", fm_text, re.M)
        desc_m = re.search(r"^description:\s*", fm_text, re.M)
        if not name_m or not desc_m:
            return False, "Missing name or description (install PyYAML for full validation)", {}
        return True, "Skill is valid (lightweight check)", {"name": name_m.group(1).strip()}

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except Exception as e:  # noqa: BLE001
        return False, f"Invalid YAML in frontmatter: {e}", {}

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary", {}

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER
    if unexpected:
        return (
            False,
            f"Unexpected frontmatter keys: {', '.join(sorted(unexpected))}",
            frontmatter,
        )

    name = frontmatter.get("name")
    desc = frontmatter.get("description")
    if not isinstance(name, str) or not name.strip():
        return False, "Missing or invalid 'name'", frontmatter
    if not isinstance(desc, str) or not desc.strip():
        return False, "Missing or invalid 'description'", frontmatter

    name = name.strip()
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"Name '{name}' must be kebab-case", frontmatter
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' has invalid hyphen placement", frontmatter
    if len(name) > 64:
        return False, f"Name too long ({len(name)} > 64)", frontmatter

    desc = desc.strip()
    if "<" in desc or ">" in desc:
        return False, "Description cannot contain angle brackets", frontmatter
    # Anthropic skill-creator hard-caps description at 1024; Grok is more lenient.
    # Warn but allow so Claude source descriptions stay pushy/trigger-rich.
    warnings = []
    if len(desc) > 1024:
        warnings.append(f"description length {len(desc)} > 1024 (Claude strict packaging)")

    compat = frontmatter.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            return False, "compatibility must be a string", frontmatter
        if len(compat) > 500:
            warnings.append(f"compatibility length {len(compat)} > 500")

    msg = "Skill is valid"
    if warnings:
        msg += " (warnings: " + "; ".join(warnings) + ")"
    return True, msg, frontmatter


def package_skill(
    skill_path: Path,
    output_dir: Path,
    runtime_md: Path | None = None,
) -> Path | None:
    skill_path = skill_path.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    ok, message, fm = validate_skill(skill_path)
    if not ok:
        print(f"❌ {skill_path.name}: {message}")
        return None
    print(f"✅ {skill_path.name}: {message}")

    skill_name = skill_path.name
    out_file = output_dir / f"{skill_name}.skill"

    # Files to write: walk skill dir + optional injected runtime doc
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if not file_path.is_file():
                continue
            arc = file_path.relative_to(skill_path.parent)
            if should_exclude(arc):
                continue
            zf.write(file_path, arcname=str(arc).replace("\\", "/"))

        # Inject shared runtime adapter if skill doesn't already ship one
        dest_arc = f"{skill_name}/references/agent-runtimes.md"
        already = any(i.filename == dest_arc for i in zf.infolist())
        if runtime_md and runtime_md.is_file() and not already:
            zf.write(runtime_md, arcname=dest_arc)
            print(f"  + injected {dest_arc}")

    print(f"📦 {out_file} ({out_file.stat().st_size} bytes)")
    return out_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a skill into a .skill zip")
    parser.add_argument("skill_path", type=Path)
    parser.add_argument("output_dir", type=Path, nargs="?", default=Path("dist/grok"))
    parser.add_argument(
        "--runtime",
        type=Path,
        default=None,
        help="Path to shared agent-runtimes.md to inject if missing",
    )
    args = parser.parse_args()

    result = package_skill(args.skill_path, args.output_dir, args.runtime)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

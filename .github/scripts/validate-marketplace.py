#!/usr/bin/env python3
"""Validate that the Copilot marketplace and packaged skills agree."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).parents[2]
MARKETPLACE_PATH = ROOT / ".github" / "plugin" / "marketplace.json"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
SKILL_NAME = re.compile(r"^name:\s*['\"]?([^'\"\r\n]+?)['\"]?\s*$", re.MULTILINE)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path.relative_to(ROOT)} is not valid JSON: {error}") from error


def skill_name(path: Path) -> str | None:
    match = SKILL_NAME.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else None


def main() -> int:
    errors: list[str] = []

    try:
        marketplace = load_json(MARKETPLACE_PATH)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("marketplace must define a non-empty plugins array")
        plugins = []

    catalog_names: set[str] = set()
    packaged_skills: set[Path] = set()
    for entry in plugins:
        name = entry.get("name") if isinstance(entry, dict) else None
        source = entry.get("source") if isinstance(entry, dict) else None
        if not isinstance(name, str) or not name:
            errors.append("marketplace plugin entry has no name")
            continue
        if name in catalog_names:
            errors.append(f"marketplace plugin name is duplicated: {name}")
        catalog_names.add(name)

        if not isinstance(source, str) or not source:
            errors.append(f"{name}: marketplace entry has no source")
            continue
        plugin_root = ROOT / source
        manifest_path = plugin_root / "plugin.json"
        if not manifest_path.is_file():
            errors.append(f"{name}: missing {manifest_path.relative_to(ROOT)}")
            continue

        try:
            manifest = load_json(manifest_path)
        except ValueError as error:
            errors.append(str(error))
            continue
        if manifest.get("$schema") != PLUGIN_SCHEMA:
            errors.append(f"{name}: plugin.json must declare the Agent Plugins 1.0 schema")
        if manifest.get("name") != name:
            errors.append(f"{name}: plugin.json name does not match marketplace entry")
        if manifest.get("version") != entry.get("version"):
            errors.append(f"{name}: plugin.json version does not match marketplace entry")

        skills_dir = plugin_root / "skills"
        if not skills_dir.is_dir():
            errors.append(f"{name}: missing skills directory")
            continue
        for skill_file in skills_dir.glob("*/SKILL.md"):
            packaged_skills.add(skill_file.resolve())
            expected_name = skill_file.parent.name
            actual_name = skill_name(skill_file)
            if actual_name != expected_name:
                errors.append(
                    f"{skill_file.relative_to(ROOT)}: frontmatter name "
                    f"{actual_name!r} does not match directory {expected_name!r}"
                )

    all_skills = {path.resolve() for path in ROOT.glob("plugins/*/skills/*/SKILL.md")}
    if packaged_skills != all_skills:
        errors.append("every packaged skill must belong to exactly one marketplace plugin")

    if errors:
        print("Marketplace validation failed:", file=sys.stderr)
        print(*[f"- {error}" for error in errors], sep="\n", file=sys.stderr)
        return 1

    print(f"Marketplace validation passed for {len(catalog_names)} plugins and {len(all_skills)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

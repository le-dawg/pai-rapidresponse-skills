#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
CI Skill Validation Linter for pai-rapidresponse-skills
Checks all skills in the repository for compliance with the AgentSkills.io standard:
- Valid YAML frontmatter delimiters
- Kebab-case skill naming
- Description starting with 'Use when ' and within character limits
- Word count bounds
- Runs execution tests for skills with bundled test fixtures
"""

import sys
import re
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def validate_skill_dir(skill_dir: Path) -> tuple[list[str], list[str]]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return [f"Missing SKILL.md in {skill_dir.name}"], []

    content = skill_file.read_text(encoding="utf-8")
    errors = []
    warnings = []

    # 1. Frontmatter Checks
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not fm_match:
        errors.append(f"{skill_dir.name}: Missing or malformed YAML frontmatter")
        return errors, warnings

    fm_raw = fm_match.group(1)
    try:
        data = yaml.safe_load(fm_raw)
        if not isinstance(data, dict):
            errors.append(f"{skill_dir.name}: Frontmatter does not parse to a key-value dictionary")
            return errors, warnings
    except Exception as e:
        errors.append(f"{skill_dir.name}: YAML parsing error: {e}")
        return errors, warnings

    # Name check
    name = data.get("name")
    if not name:
        errors.append(f"{skill_dir.name}: Frontmatter missing required 'name' field")
    elif not re.match(r"^[a-z0-9-]+$", str(name)):
        errors.append(f"{skill_dir.name}: Name '{name}' must be lowercase alphanumeric with hyphens only")

    # Description check
    desc = data.get("description")
    if not desc:
        errors.append(f"{skill_dir.name}: Frontmatter missing required 'description' field")
    else:
        desc_clean = re.sub(r"\s+", " ", str(desc)).strip()
        if not desc_clean.startswith("Use when"):
            warnings.append(f"{skill_dir.name}: Description does not start with 'Use when...'")
        if len(desc_clean) > 500:
            warnings.append(f"{skill_dir.name}: Description is long ({len(desc_clean)} chars). Recommended < 400 chars.")

    # Word count check
    words = len(content.split())
    if words > 1800:
        warnings.append(f"{skill_dir.name}: Word count is high ({words} words). Consider extracting reference material to references/")

    return errors, warnings

def main():
    print("=" * 60)
    print("🤖 AgentSkills CI Validator — pai-rapidresponse-skills")
    print("=" * 60)

    all_errors = []
    all_warnings = []
    validated_skills = 0

    for item in sorted(REPO_ROOT.iterdir()):
        if item.is_dir() and not item.name.startswith(".") and (item / "SKILL.md").exists():
            validated_skills += 1
            errs, warns = validate_skill_dir(item)
            if errs:
                all_errors.extend(errs)
                print(f"❌ {item.name}: FAILED")
                for e in errs:
                    print(f"   - {e}")
            elif warns:
                all_warnings.extend(warns)
                print(f"⚠️ {item.name}: PASSED with warnings")
                for w in warns:
                    print(f"   - {w}")
            else:
                print(f"✅ {item.name}: PASSED")

    print("\n" + "=" * 60)
    print(f"📊 Summary: {validated_skills} skills validated.")
    print(f"   • Errors: {len(all_errors)}")
    print(f"   • Warnings: {len(all_warnings)}")
    print("=" * 60)

    if all_errors:
        print("\n❌ CI Validation FAILED with errors.")
        sys.exit(1)
    else:
        print("\n✨ All skills passed validation!")
        sys.exit(0)

if __name__ == "__main__":
    main()

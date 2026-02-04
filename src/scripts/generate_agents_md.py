#!/usr/bin/env python3
"""Generate AGENTS.md from .cursor/rules/, .cursor/skills/, canonical-sources.md."""

import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_file(path: Path) -> str:
    if not path.exists():
        log.warning(f"File not found: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        log.warning(f"Error reading {path}: {e}")
        return ""


def extract_frontmatter(content: str) -> dict[str, str]:
    if not content:
        return {}
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip()
    return fm


def extract_title(content: str) -> str:
    if not content:
        return ""
    match = re.search(r"^#\s+(.+?)(?:\s+\(v[\d.]+\))?$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_section(content: str, header_pattern: str, level: int = 2) -> str:
    if not content:
        return ""
    hashes = "#" * level
    pattern = rf"^{hashes}\s*{header_pattern}.*?\n(.*?)(?=^#{{{level}}}\s|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        log.warning(f"Section not found: {header_pattern}")
        return ""
    return match.group(1).strip()


def extract_list_items(section: str) -> list[str]:
    if not section:
        return []
    return [line.strip() for line in section.split("\n") if line.strip().startswith("-")]


def extract_numbered_items(section: str) -> list[str]:
    """Extract numbered items, including continuation lines."""
    if not section:
        return []
    items = []
    current_item: list[str] = []
    for line in section.split("\n"):
        stripped = line.strip()
        if re.match(r"^\d+\.\s", stripped):
            if current_item:
                items.append(" ".join(current_item))
            current_item = [stripped]
        elif current_item and stripped and not stripped.startswith(("#", "-")):
            current_item.append(stripped)
    if current_item:
        items.append(" ".join(current_item))
    return items


def extract_code_block(section: str) -> str:
    if not section:
        return ""
    match = re.search(r"```(?:text)?\s*\n(.*?)```", section, re.DOTALL)
    return match.group(1).strip() if match else ""


def discover_skills(skills_dir: Path) -> list[tuple[str, str]]:
    """Discover skills and read labels from SKILL.md frontmatter or title."""
    if not skills_dir.exists():
        log.warning(f"Skills directory not found: {skills_dir}")
        return []
    skills = []
    for skill_path in sorted(skills_dir.iterdir()):
        skill_file = skill_path / "SKILL.md"
        if skill_path.is_dir() and skill_file.exists():
            content = read_file(skill_file)
            title = extract_title(content)
            label = title.replace(" (Skill)", "").strip() if title else skill_path.name
            skills.append((label, skill_path.name))
    return skills


def generate_skills_table(skills: list[tuple[str, str]]) -> str:
    lines = ["| Задача | Skill |", "| ------ | ----- |"]
    for label, skill_id in skills:
        lines.append(f"| {label} | `{skill_id}` |")
    return "\n".join(lines)


def generate_paths_table(paths_section: str) -> str:
    lines = ["| Артефакт | Путь |", "| -------- | ---- |"]
    for item in extract_list_items(paths_section):
        match = re.match(r"-\s*(.+?):\s*`(.+?)`", item)
        if match:
            lines.append(f"| {match.group(1)} | `{match.group(2)}` |")
    return "\n".join(lines)


def generate_commands_section(package_json: dict) -> str:
    scripts = package_json.get("scripts", {})
    lines = ["```bash"]
    for name in scripts:
        lines.append(f"npm run {name}")
    lines.append("python3 src/scripts/export_png_white.py")
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    root = repo_root()
    rules_dir = root / ".cursor" / "rules"
    skills_dir = root / ".cursor" / "skills"

    project_core = read_file(rules_dir / "project-core.mdc")
    assistant_style = read_file(rules_dir / "assistant-style.mdc")
    ai_protocols = read_file(rules_dir / "ai-protocols.mdc")
    canonical = read_file(root / "canonical-sources.md")

    pkg_path = root / "package.json"
    package_json = json.loads(read_file(pkg_path)) if pkg_path.exists() else {}

    fm = extract_frontmatter(project_core)
    version = fm.get("version", "1.0")
    today = date.today().isoformat()

    title = extract_title(project_core)
    project_name = title.split("-")[0].strip().replace("Ядро проекта ", "")
    if not project_name:
        project_name = "Project"

    lang_section = extract_section(assistant_style, r"1\)\s*Язык и тон")
    lang_items = "\n".join(extract_list_items(lang_section))

    principles_section = extract_section(project_core, r"1\)\s*Принципы работы")
    principles_items = "\n".join(extract_list_items(principles_section))

    rules_section = extract_section(project_core, r"4\)\s*Неизменные правила")
    rules_items = "\n".join(extract_numbered_items(rules_section))

    priority_section = extract_section(canonical, r"Приоритет информации")
    priority_items = "\n".join(extract_list_items(priority_section))
    priority_note_match = re.search(
        r"(Если какой-либо документ.*?приоритет.*?)$",
        priority_section,
        re.MULTILINE,
    )
    priority_note = priority_note_match.group(1) if priority_note_match else ""

    paths_section = extract_section(canonical, r"Каноничные пути \(SSOT\)")
    paths_table = generate_paths_table(paths_section)

    stopcrane_section = extract_section(
        ai_protocols, r"3\.\s*Протокол верификации", level=3
    )
    stopcrane_block = extract_code_block(stopcrane_section)

    skills = discover_skills(skills_dir)
    skills_table = generate_skills_table(skills)

    commands = generate_commands_section(package_json)

    output = f"""---
version: {version}
lastUpdated: {today}
status: Активен
---

# AGENTS.md — Инструкции для AI-агентов (v{version})

> Проект: **{project_name}** — шаблон для проектирования информационных систем.
>
> **Автогенерация**: `npm run gen:agents` из `.cursor/rules/` и `.cursor/skills/`.

## Язык и стиль

{lang_items}

## Ключевые принципы

{principles_items}

## Неизменные правила

{rules_items}

## Каноничные пути

{paths_table}

## Приоритет документов

{priority_items}

{priority_note}

## Skills (`.cursor/skills/`)

{skills_table}

## Перед сложными изменениями

Выполнить "стоп‑кран" (см. `.cursor/rules/ai-protocols.mdc`):

```text
{stopcrane_block}
```

## Команды

{commands}
"""

    agents_path = root / "AGENTS.md"
    agents_path.write_text(output, encoding="utf-8")
    log.info(f"Generated {agents_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate AGENTS.md from .cursor/rules/, .cursor/skills/, canonical-sources.md."""

import json
import re
from datetime import date
from pathlib import Path

SKILL_LABELS = {
    "adr-authoring": "ADR",
    "ai-protocols": "AI протоколы",
    "architecture-review": "Финальный review",
    "c4-modeling": "C4 моделирование",
    "capacity-planning": "Нагрузка",
    "data-architecture": "Данные",
    "domain-modeling-ddd": "DDD",
    "export-likec4-png-white": "Экспорт PNG",
    "integration-patterns": "Интеграции",
    "likec4-workflow": "LikeC4 workflow",
    "markdownlint-workflow": "Markdown lint",
    "nfr-design": "NFR/SLO",
    "observability-architecture": "Наблюдаемость",
    "repo-hygiene": "Гигиена репо",
    "scaffold-examples": "Scaffold примеров",
    "security-architecture": "Безопасность",
    "system-design": "Координация",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def extract_frontmatter(content: str) -> dict[str, str]:
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
    match = re.search(r"^#\s+(.+?)(?:\s+\(v[\d.]+\))?$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_section(content: str, header_pattern: str, level: int = 2) -> str:
    hashes = "#" * level
    pattern = rf"^{hashes}\s*{header_pattern}.*?\n(.*?)(?=^#{{{level}}}\s|\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_list_items(section: str) -> list[str]:
    return [line.strip() for line in section.split("\n") if line.strip().startswith("-")]


def extract_numbered_items(section: str) -> list[str]:
    return [
        line.strip()
        for line in section.split("\n")
        if re.match(r"^\d+\.\s", line.strip())
    ]


def extract_code_block(section: str) -> str:
    match = re.search(r"```(?:text)?\s*\n(.*?)```", section, re.DOTALL)
    return match.group(1).strip() if match else ""


def discover_skills(skills_dir: Path) -> list[tuple[str, str]]:
    skills = []
    for skill_path in sorted(skills_dir.iterdir()):
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            name = skill_path.name
            label = SKILL_LABELS.get(name, name)
            skills.append((label, name))
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
    for name, cmd in scripts.items():
        lines.append(f"npm run {name}")
    lines.append("python3 src/scripts/export_png_white.py")
    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    root = repo_root()
    rules_dir = root / ".cursor" / "rules"
    skills_dir = root / ".cursor" / "skills"

    project_core = (rules_dir / "project-core.mdc").read_text(encoding="utf-8")
    assistant_style = (rules_dir / "assistant-style.mdc").read_text(encoding="utf-8")
    ai_protocols = (rules_dir / "ai-protocols.mdc").read_text(encoding="utf-8")
    canonical = (root / "canonical-sources.md").read_text(encoding="utf-8")
    package_json = json.loads((root / "package.json").read_text(encoding="utf-8"))

    fm = extract_frontmatter(project_core)
    version = fm.get("version", "1.0")
    today = date.today().isoformat()

    title = extract_title(project_core)
    project_name = title.split("-")[0].strip().replace("Ядро проекта ", "")

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
        extract_section(canonical, r"Приоритет информации"),
        re.MULTILINE,
    )
    priority_note = priority_note_match.group(1) if priority_note_match else ""

    paths_section = extract_section(canonical, r"Каноничные пути \(SSOT\)")
    paths_table = generate_paths_table(paths_section)

    stopcrane_section = extract_section(ai_protocols, r"3\.\s*Протокол верификации", level=3)
    stopcrane_block = extract_code_block(stopcrane_section)

    skills = discover_skills(skills_dir)
    skills_table = generate_skills_table(skills)

    commands = generate_commands_section(package_json)

    output = f"""---
version: {version}
lastUpdated: {today}
status: Активен
generated: true
---

# AGENTS.md — Инструкции для AI-агентов (v{version})

> Проект: **{project_name}** — шаблон для проектирования информационных систем.
>
> **Автогенерация**: этот файл генерируется из `.cursor/rules/` и `.cursor/skills/`.
> Не редактируйте вручную — используйте `npm run gen:agents`.

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
    print(f"Generated {agents_path}")


if __name__ == "__main__":
    main()

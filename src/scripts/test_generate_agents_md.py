#!/usr/bin/env python3
"""Tests for generate_agents_md.py."""

import tempfile
from pathlib import Path

import generate_agents_md as gen


def test_extract_frontmatter_valid():
    content = """---
version: 1.0
lastUpdated: 2026-02-04
status: Активен
---

# Title
"""
    fm = gen.extract_frontmatter(content)
    assert fm["version"] == "1.0"
    assert fm["lastUpdated"] == "2026-02-04"
    assert fm["status"] == "Активен"


def test_extract_frontmatter_empty():
    assert gen.extract_frontmatter("") == {}
    assert gen.extract_frontmatter("no frontmatter") == {}


def test_extract_title_with_version():
    content = "# My Title (v1.0)\n\nContent"
    assert gen.extract_title(content) == "My Title"


def test_extract_title_without_version():
    content = "# Simple Title\n\nContent"
    assert gen.extract_title(content) == "Simple Title"


def test_extract_title_empty():
    assert gen.extract_title("") == ""
    assert gen.extract_title("no title here") == ""


def test_extract_section_level2():
    content = """## Section One

Content of section one.

## Section Two

Content of section two.
"""
    result = gen.extract_section(content, "Section One")
    assert "Content of section one" in result
    assert "Section Two" not in result


def test_extract_section_level3():
    content = """### 1. First

First content.

### 2. Second

Second content.
"""
    result = gen.extract_section(content, r"1\.\s*First", level=3)
    assert "First content" in result
    assert "Second content" not in result


def test_extract_section_not_found():
    content = "## Existing\n\nContent"
    result = gen.extract_section(content, "NonExistent")
    assert result == ""


def test_extract_list_items():
    section = """Some intro text.

- First item
- Second item
- Third item

Some outro.
"""
    items = gen.extract_list_items(section)
    assert len(items) == 3
    assert items[0] == "- First item"
    assert items[2] == "- Third item"


def test_extract_list_items_empty():
    assert gen.extract_list_items("") == []
    assert gen.extract_list_items("no list here") == []


def test_extract_numbered_items_simple():
    section = """1. First rule
2. Second rule
3. Third rule
"""
    items = gen.extract_numbered_items(section)
    assert len(items) == 3
    assert items[0] == "1. First rule"


def test_extract_numbered_items_multiline():
    section = """1. First rule with
   continuation on next line
2. Second rule
"""
    items = gen.extract_numbered_items(section)
    assert len(items) == 2
    assert "continuation" in items[0]
    assert items[1] == "2. Second rule"


def test_extract_numbered_items_empty():
    assert gen.extract_numbered_items("") == []


def test_extract_code_block():
    section = """Some text.

```text
Code content here.
Multiple lines.
```

More text.
"""
    result = gen.extract_code_block(section)
    assert "Code content here" in result
    assert "Multiple lines" in result


def test_extract_code_block_empty():
    assert gen.extract_code_block("") == ""
    assert gen.extract_code_block("no code block") == ""


def test_discover_skills(tmp_path: Path):
    skill_dir = tmp_path / "skills"
    skill_dir.mkdir()

    skill1 = skill_dir / "my-skill"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("# My Skill Title (Skill)\n\nContent")

    skill2 = skill_dir / "another-skill"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text("# Another One\n\nContent")

    skills = gen.discover_skills(skill_dir)
    assert len(skills) == 2
    labels = [s[0] for s in skills]
    assert "Another One" in labels
    assert "My Skill Title" in labels


def test_discover_skills_empty(tmp_path: Path):
    skill_dir = tmp_path / "skills"
    skill_dir.mkdir()
    assert gen.discover_skills(skill_dir) == []


def test_discover_skills_missing_dir(tmp_path: Path):
    assert gen.discover_skills(tmp_path / "nonexistent") == []


def test_generate_skills_table():
    skills = [("Label One", "skill-one"), ("Label Two", "skill-two")]
    table = gen.generate_skills_table(skills)
    assert "| Задача | Skill |" in table
    assert "| Label One | `skill-one` |" in table
    assert "| Label Two | `skill-two` |" in table


def test_generate_paths_table():
    section = """- First: `path/one/`
- Second: `path/two/`
"""
    table = gen.generate_paths_table(section)
    assert "| First | `path/one/` |" in table
    assert "| Second | `path/two/` |" in table


def test_generate_commands_section():
    pkg = {"scripts": {"lint": "echo lint", "build": "echo build"}}
    result = gen.generate_commands_section(pkg)
    assert "npm run lint" in result
    assert "npm run build" in result
    assert "export_png_white.py" in result


if __name__ == "__main__":
    import sys

    failed = 0
    for name, func in list(globals().items()):
        if name.startswith("test_") and callable(func):
            try:
                if "tmp_path" in func.__code__.co_varnames:
                    with tempfile.TemporaryDirectory() as td:
                        func(Path(td))
                else:
                    func()
                print(f"✓ {name}")
            except AssertionError as e:
                print(f"✗ {name}: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {name}: {type(e).__name__}: {e}")
                failed += 1
    sys.exit(failed)

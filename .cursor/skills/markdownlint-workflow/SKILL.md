---
name: markdownlint-workflow
description: Единый workflow markdownlint для репозитория (конфиг, запуск, типовые правки).
version: 1.0
lastUpdated: 2026-02-04
---

# Markdownlint Workflow (Skill)

## Каноничный конфиг

- `.markdownlint.json` в корне репозитория.

## Как запускать

```bash
npx --yes markdownlint-cli2 "**/*.{md,mdc}"
```

## Типовые ошибки и исправления

- **MD013 (line-length)**: переносить строки, не раздувать абзацы.
- **MD022/MD032**: пустые строки вокруг заголовков и списков.
- **MD031/MD040**: fenced blocks окружать пустыми строками и указывать язык.
- **MD010**: не использовать табы, только пробелы.

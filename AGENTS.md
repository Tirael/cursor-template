# AGENTS.md — Инструкции для AI-агентов

> Проект: **EBookStore** — шаблон для проектирования интернет-магазина электронных книг.

## Язык и стиль

- **Язык**: русский (если не указано иное).
- **Тон**: инженерный, прямой, без "воды".
- **Код**: минимализм, без комментариев, только релевантные фрагменты.

## Ключевые принципы

1. **Итеративность**: только текущая задача, маленькие шаги.
2. **DDD**: доменная логика изолирована, bounded context не размывать.
3. **Production-ready**: без временных решений.
4. **Tenant isolation**: любые чтения/записи учитывают `tenantId`.
5. **Идемпотентность**: команды используют `correlationId` (UUIDv7).
6. **Секреты**: только Vault, запрет секретов в репозитории.
7. **Аудит**: операции записи фиксируются в `audit_log`.

## Каноничные пути

| Артефакт | Путь |
| -------- | ---- |
| C4/LikeC4 диаграммы | `src/c4/` |
| PlantUML диаграммы | `src/diagrams/` |
| Скрипты | `src/scripts/` |
| Примеры кода | `src/examples/` |
| Чек‑листы | `checklists/` |
| Упражнения | `design-exercises/` |

## Приоритет документов

1. **Core (SSOT)**: `.cursor/rules/nfr-core.mdc`, `.cursor/rules/project-core.mdc`
2. **Reference**: `nfr-requirements.md`, `adr-architecture-decisions.md`
3. **Остальное**: при конфликте — Core имеет приоритет.

## Ключевые документы

- **Framework проектирования**: `system-design-framework.md`
- **Trade-offs**: `tradeoffs.md`
- **Каноничные пути**: `canonical-sources.md`

## Skills (`.cursor/skills/`)

| Задача | Skill |
| ------ | ----- |
| C4 моделирование | `c4-modeling` |
| DDD | `domain-modeling-ddd` |
| NFR/SLO | `nfr-design` |
| Интеграции | `integration-patterns` |
| Безопасность | `security-architecture` |
| Данные | `data-architecture` |
| Наблюдаемость | `observability-architecture` |
| Нагрузка | `capacity-planning` |
| ADR | `adr-authoring` |
| Финальный review | `architecture-review` |
| Координация | `system-design` |

## Перед сложными изменениями

Выполнить "стоп‑кран" (см. `.cursor/rules/ai-protocols.mdc`):

1. Что именно меняем?
2. Какие документы/компоненты затронуты?
3. Какие принципы/NFR нужно учесть?
4. Какие последствия?

## Команды

```bash
# Линтинг документации
npx --yes markdownlint-cli2 "**/*.{md,mdc}"

# Экспорт C4 диаграмм в PNG
python3 src/scripts/export_png_white.py

# Запуск LikeC4
docker run --rm -v $PWD/src/c4:/data -p 5173:5173 likec4/likec4:1.48.0 start
```

---
version: 1.0
lastUpdated: 2026-02-04
status: Активен
generated: true
---

# AGENTS.md — Инструкции для AI-агентов (v1.0)

> Проект: **EBookStore** — шаблон для проектирования информационных систем.
>
> **Автогенерация**: этот файл генерируется из `.cursor/rules/` и `.cursor/skills/`.
> Не редактируйте вручную — используйте `npm run gen:agents`.

## Язык и стиль

- **Язык**: всегда русский (если пользователь явно не попросил иначе).
- **Тон**: инженерный, прямой, без “воды” и теоретических лекций.
- **Не делать**: не использовать эмодзи; не “угадывать” требования.

## Ключевые принципы

- **Итеративность**: только текущая задача, маленькие шаги, без “задела”
- **DDD**: доменная логика изолирована, bounded context не размывать
- **Production-ready**: без временных решений
- **Async-first**: `async/await` и `CancellationToken` вниз по стеку
- **Детерминизм**: команды идемпотентны (см. раздел 4)

## Неизменные правила

1. **Tenant isolation**: любые чтения/записи обязаны учитывать `tenantId`
2. **ABAC**: чувствительные операции проверяют `tenantId` + роль
3. **Идемпотентность**: команды используют `correlationId` (UUIDv7)
4. **Длительные операции (>5 сек)**: только асинхронно через Quartz.NET
5. **Integration Events**: публикация только через Transactional Outbox
6. **Шифрование**: HTTPS/TLS; mTLS для внутренних gRPC
7. **Секреты**: только Vault; запрет секретов в репозитории
8. **Аудит**: операции записи фиксируются в `audit_log` (минимум:

## Каноничные пути

| Артефакт | Путь |
| -------- | ---- |
| C4/LikeC4 | `src/c4/` |
| PlantUML (диаграммы последовательностей и пр.) | `src/diagrams/` |
| Скрипты | `src/scripts/` |
| Примеры проектов/кода | `src/examples/` |
| Экспорт PNG | `png/` |
| Чек‑листы | `checklists/` |

## Приоритет документов

- **Core (обязательные правила, SSOT)**:
- `.cursor/rules/nfr-core.mdc` (v1.0, lastUpdated: 2026-02-04)
- `.cursor/rules/project-core.mdc` (v1.0, lastUpdated: 2026-02-04)
- **Reference**:
- `nfr-requirements.md` (v1.0, lastUpdated: 2026-02-04)

Если какой-либо документ расходится с Core — **Core имеет приоритет**.

## Skills (`.cursor/skills/`)

| Задача | Skill |
| ------ | ----- |
| ADR | `adr-authoring` |
| AI протоколы | `ai-protocols` |
| Финальный review | `architecture-review` |
| C4 моделирование | `c4-modeling` |
| Нагрузка | `capacity-planning` |
| Данные | `data-architecture` |
| DDD | `domain-modeling-ddd` |
| Экспорт PNG | `export-likec4-png-white` |
| Интеграции | `integration-patterns` |
| LikeC4 workflow | `likec4-workflow` |
| Markdown lint | `markdownlint-workflow` |
| NFR/SLO | `nfr-design` |
| Наблюдаемость | `observability-architecture` |
| Гигиена репо | `repo-hygiene` |
| Scaffold примеров | `scaffold-examples` |
| Безопасность | `security-architecture` |
| Координация | `system-design` |

## Перед сложными изменениями

Выполнить "стоп‑кран" (см. `.cursor/rules/ai-protocols.mdc`):

```text
Перед выполнением задачи, остановись и перескажи:
1. Какую задачу ты понял?
2. Какие документы/компоненты будут затронуты?
3. Какие существующие принципы/NFR должны быть учтены?
4. Какие последствия могут быть у этих изменений?

Только после этого переходи к выполнению.
```

## Команды

```bash
npm run lint:md
npm run gen:agents
python3 src/scripts/export_png_white.py
```

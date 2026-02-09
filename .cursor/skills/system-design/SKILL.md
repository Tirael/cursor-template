---
name: system-design
description: >-
  Координирующий skill для архитектурного проектирования.
  Определяет какие skills применять для C4, PlantUML, DDD, NFR, интеграций.
version: 1.0
lastUpdated: 2026-02-04
---

# System Design (Skill)

## Когда применять

- Начинаем проектирование новой системы или модуля
- Нужно выбрать подходящий инструмент/skill для задачи

## Карта skills по задачам

| Задача | Skill |
| ------ | ----- |
| Контекст системы (C4 Level 1) | `c4-modeling` |
| Контейнеры (C4 Level 2) | `c4-modeling` |
| Компоненты (C4 Level 3) | `c4-modeling` |
| Запуск LikeC4, экспорт PNG | `likec4-workflow`, `export-likec4-png-white` |
| C4 диаграммы в draw.io формате | `c4-drawio-diagramming` |
| Диаграммы последовательностей (PlantUML) | см. путь `src/diagrams/` |
| Bounded contexts, агрегаты, события | `domain-modeling-ddd` |
| Архитектурные решения (ADR) | `adr-authoring` |
| NFR, SLO/SLI | `nfr-design` |
| Интеграции между модулями | `integration-patterns` |
| Безопасность | `security-architecture` |
| Хранение данных | `data-architecture` |
| Наблюдаемость | `observability-architecture` |
| Оценка нагрузки | `capacity-planning` |
| Финальная проверка | `architecture-review` |

## Каноничные пути

См. `canonical-sources.md` — единый источник истины для путей.

## Правило

Перед началом работы определить, какие skills нужны, и применять их последовательно.

## Минимальный порядок работы (шаблон)

1. `ai-protocols`: “стоп‑кран” для сложных изменений.
2. `c4-modeling`: C4 Context + Container в `src/c4/` (минимум 2 views).
3. `domain-modeling-ddd`: bounded contexts, агрегаты, события (как список артефактов).
4. `nfr-design`: зафиксировать core (`.cursor/rules/nfr-core.mdc`) и полную версию (`nfr-requirements.md`).
5. `integration-patterns`: выбрать sync/async контракты и правила идемпотентности.
6. `security-architecture`: модель доступа (ABAC/tenantId), аудит, TLS/mTLS.
7. `data-architecture`: разнести данные по контекстам, кэш/поиск, миграции.
8. `observability-architecture`: поля логов/метрики/трейсы/health + SLI.
9. `capacity-planning`: таблица нагрузки + квоты + деградации.
10. `adr-authoring`: если есть выбор вариантов — запись в `adr-architecture-decisions.md`.
11. `architecture-review`: финальный проход чек-листа перед фиксацией результата.

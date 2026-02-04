---
version: 1.0
lastUpdated: 2026-02-04
status: Активен
---

# Диаграммы PlantUML (v1.0)

В этой папке хранятся диаграммы, не относящиеся к C4 модели:

- Диаграммы последовательностей (sequence)
- Диаграммы состояний (state)
- Диаграммы активностей (activity)
- Прочие UML-диаграммы

## Формат

- Исходники: `.puml` файлы
- Экспорт: `.png` или `.svg` (опционально)

## Правила

- Каждая диаграмма имеет осмысленное имя файла.
- Для сложных сценариев использовать отдельные файлы, а не один большой.

## Шаблоны (`templates/`)

| Шаблон | Назначение |
| ------ | ---------- |
| `sequence-template.puml` | Базовый запрос-ответ с correlationId |
| `retry-timeout-cb.puml` | Retry, timeout, circuit breaker |
| `async-job.puml` | Асинхронная задача через очередь |
| `outbox.puml` | Transactional Outbox pattern |
| `saga.puml` | Saga orchestration с компенсациями |
| `event-sourcing.puml` | Event Sourcing: команда → события → проекция |
| `cqrs.puml` | CQRS: разделение write/read paths |

## Пример использования

```bash
# Генерация PNG из PlantUML
docker run --rm -v $PWD:/data plantuml/plantuml:1.2026.1 templates/sequence-template.puml
```

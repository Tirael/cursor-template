---
version: 1.0
lastUpdated: 2026-02-04
status: Активен
---

# Инструкции по работе с архитектурной документацией EBookStore (v1.0)

## 0. СТРУКТУРА КАТАЛОГОВ

- Диаграммы C4/LikeC4: `src/c4/`
- Диаграммы PlantUML: `src/diagrams/`
- Скрипты репозитория: `src/scripts/`
- Примеры проектов/кода (.NET/Angular/Python): `src/examples/`
- Чек‑листы: `checklists/`

## 1. ЗАПУСК LIKEC4 В DOCKER

```shell
docker run --rm \
  -v $PWD/src/c4:/data \
  --init \
  -t \
  -p 5173:5173 \
  -p 24678:24678 \
  -e CHOKIDAR_USEPOLLING=1 \
  -e CHOKIDAR_INTERVAL=200 \
  likec4/likec4:1.48.0 \
  start
```

---

## 2. КОМАНДЫ

```bash
npx --yes markdownlint-cli2 "**/*.{md,mdc}"
python3 src/scripts/export_png_white.py
```

---

## 3. ШАБЛОНЫ ПРОЕКТИРОВАНИЯ

- Framework: `system-design-framework.md`
- Trade-offs: `tradeoffs.md`
- Чек‑листы: `checklists/`

---

## История версий

### v1.0 (2025-01-27)

- Начальная версия документа
- Добавлено версионирование согласно протоколам работы с AI
- Инструкции по запуску LikeC4 в Docker

---
name: likec4-workflow
description: Workflow для LikeC4/C4 диаграмм (хранение, запуск, экспорт PNG).
version: 1.0
lastUpdated: 2026-02-04
---

# LikeC4 Workflow (Skill)

## Где храним

- Модель и views: `src/c4/`

## Как запустить визуализацию

```bash
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

## Как экспортировать PNG

Базовая команда:

```bash
python3 src/scripts/export_png_white.py
```

Детальное описание опций, ошибок и вариантов запуска —
см. skill `export-likec4-png-white`.

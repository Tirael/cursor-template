---
version: 1.1
lastUpdated: 2026-02-11
status: Активен
---

# Скрипты репозитория (v1.1)

## `export_png_white.py`

Экспортирует LikeC4 диаграммы в PNG и приводит фон к белому.

Запуск из корня репозитория:

```bash
python3 src/scripts/export_png_white.py
```

## `c4_drawio_autolayout.py`

Генерирует `.drawio` (diagrams.net) файл из JSON/YAML спека: размещает элементы без пересечений и трассирует ортогональные соединения без пересечения с элементами и уже проложенными соединениями.

Запуск из корня репозитория:

```bash
python3 src/scripts/c4_drawio_autolayout.py \
  --input src/examples/python-c4-drawio/spec.json \
  --output src/examples/python-c4-drawio/out.drawio
```

---

## История версий

### v1.1 (2026-02-11)

- Добавлен `c4_drawio_autolayout.py` (генерация draw.io + auto-layout + routing).

### v1.0 (2026-02-04)

- Начальная версия: `export_png_white.py`.

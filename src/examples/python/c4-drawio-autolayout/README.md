---
version: 1.0
lastUpdated: 2026-02-11
status: Активен
---

# Пример: генерация C4-like draw.io (v1.0)

Этот пример показывает формат входного спека и генерацию `.drawio` файла с авто‑размещением и трассировкой соединений.

## Запуск

Из корня репозитория:

```bash
python3 src/scripts/c4_drawio_autolayout.py \
  --input src/examples/python/c4-drawio-autolayout/spec.json \
  --output src/examples/python/c4-drawio-autolayout/out.drawio
```

Откройте `out.drawio` в diagrams.net (draw.io).

## Контекстная диаграмма (System Context)

Генерация:

```bash
python3 src/scripts/c4_drawio_autolayout.py \
  --input src/examples/python/c4-drawio-autolayout/spec_context.json \
  --output src/examples/python/c4-drawio-autolayout/context.drawio \
  --h-gap 320 --v-gap 140 --node-pad 14 --reserve-radius 0 --expand-tries 14
```

## Формат спека (кратко)

- `diagram.name`: имя страницы в draw.io
- `nodes[]`: элементы (id/label/kind/width/height)
- `edges[]`: связи (source/target/label)

`kind` влияет на стиль (Person/SoftwareSystem/Container/Component).


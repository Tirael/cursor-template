---
name: export-likec4-png-white
description: Экспортирует и пересобирает диаграммы LikeC4 в PNG с белым фоном
  через src/scripts/export_png_white.py.
version: 1.0
lastUpdated: 2026-02-04
---

# Экспорт LikeC4 в PNG с белым фоном

## Когда применять

- Пользователь просит выгрузить LikeC4/C4 диаграммы в PNG
- Нужны PNG с белым фоном (печать, документы, вставка в слайды)
- Нужно обновить экспортированные диаграммы после изменений модели

## Выполнение

Запуск из корня репозитория (workspace):

```bash
python3 src/scripts/export_png_white.py
```

**Опции:**

- `--flatten-only` — только наложить белый фон на уже экспортированные PNG в
  `png/`, не вызывать likec4
- `--use-dot` — экспорт через graphviz (`dot` в PATH); использовать, если likec4
  падает с `uv_interface_addresses` при запуске preview-сервера

**Что делает скрипт:**

1. Проверяет модель: `likec4 validate src/c4`
2. Экспортирует PNG в светлой теме:
   `likec4 export png --theme light -o ./png src/c4`
   (при наличии `--use-dot` добавляет `--use-dot`)
3. Накладывает белый фон на все PNG (Pillow), сохраняет в `./png`
4. Удаляет `png/index.png`, если он есть

**Результат:** все PNG диаграмм в каталоге `png/` с непрозрачным белым фоном.

## Требования

- **likec4** в PATH (CLI LikeC4)
- **Python 3** с доступом к pip (для установки Pillow при первом запуске)
- Pillow при необходимости устанавливается скриптом в `.tools/pillow`

## Ошибки

- `likec4 not found in PATH` — установить/добавить в PATH CLI LikeC4
- `python3 not found` — использовать среду с Python 3
- Ошибки валидации — исправить модель в `src/c4/` по выводу `likec4 validate`
- `uv_interface_addresses returned Unknown system error 1` при экспорте —
  запустить с `--use-dot` (нужен `dot` в PATH) или экспорт вручную:
  `likec4 export png --theme light --use-dot -o ./png src/c4`,
  затем `python3 src/scripts/export_png_white.py --flatten-only`

## Как пересобирать PNG

**Полная пересборка** (модель в `src/c4/` изменилась, нужны свежие PNG
с белым фоном):

1. Из корня репозитория: `python3 src/scripts/export_png_white.py`
2. Если падает с `uv_interface_addresses` — см. вариант ниже «Без preview-сервера».

**Только белый фон** (PNG уже есть в `png/`, нужно только наложить белый фон):

```bash
python3 src/scripts/export_png_white.py --flatten-only
```

При первом запуске скрипт установит Pillow в `.tools/pillow`.
Может потребоваться сеть и до 1–2 минут.

**Без preview-сервера** (когда `likec4 export png` падает с `uv_interface_addresses`):

1. Экспорт через graphviz (нужен `dot` в PATH):  
   `likec4 export png --theme light --use-dot -o ./png src/c4`
2. Наложение белого фона:  
   `python3 src/scripts/export_png_white.py --flatten-only`

**Результат:** контекстные и контейнерные диаграммы в `png/views/`
(например `context.png`, `containerBFF.png`, …) с непрозрачным белым фоном.
Файл `png/index.png` после скрипта удаляется.

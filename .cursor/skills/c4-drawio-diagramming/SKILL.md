---
name: c4-drawio-diagramming
description: >-
  Генерация C4 Model диаграмм (Context, Container, Component) в формате
  draw.io XML с оптимальным размещением элементов без пересечений.
version: 1.0
lastUpdated: 2026-02-09
---

# C4 Draw.io Diagramming (Skill)

## Когда применять

- Нужна C4 диаграмма в формате draw.io (`.drawio` XML)
- Требуется оптимальное размещение элементов без пересечений
- Нужна диаграмма, совместимая с app.diagrams.net и VS Code draw.io plugin
- Создание диаграмм для документации, презентаций, README

## Где хранить артефакты

- Draw.io диаграммы: `src/diagrams/drawio/`
- Именование: `c4-{level}-{scope}.drawio`
  - `c4-context-ebookstore.drawio`
  - `c4-container-ebookstore.drawio`
  - `c4-component-catalog.drawio`

## 1. Стили элементов C4

### 1.1 Person (Пользователь / Актор)

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#08427B;fontColor=#ffffff;
strokeColor=#073763;fontSize=13;arcSize=50;verticalAlign=middle;
align=center;spacing=8;
```

- **Размер**: 200 × 180 px
- **Цвет**: `#08427B` (тёмно-синий)
- **Текст**: белый, 13px

### 1.2 Software System (Внутренняя система)

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#1168BD;fontColor=#ffffff;
strokeColor=#0B4884;fontSize=14;arcSize=10;verticalAlign=middle;
align=center;spacing=8;
```

- **Размер**: 280–400 × 180–200 px
- **Цвет**: `#1168BD` (синий)

### 1.3 External System (Внешняя система)

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#999999;fontColor=#ffffff;
strokeColor=#6D6D6D;fontSize=13;arcSize=10;verticalAlign=middle;
align=center;spacing=8;
```

- **Размер**: 240 × 160 px
- **Цвет**: `#999999` (серый)

### 1.4 Container (Контейнер)

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#438DD5;fontColor=#ffffff;
strokeColor=#3C7FC0;fontSize=12;arcSize=10;verticalAlign=middle;
align=center;spacing=6;
```

- **Размер**: 200 × 120–140 px
- **Цвет**: `#438DD5` (средне-синий)

### 1.5 Container — Database (Цилиндр)

```text
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#438DD5;fontColor=#ffffff;
strokeColor=#3C7FC0;fontSize=12;size=15;verticalAlign=middle;
align=center;spacing=6;
```

- **Размер**: 200 × 90–100 px
- **Форма**: `shape=cylinder3`

### 1.6 Container — Queue / Message Broker

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#438DD5;fontColor=#ffffff;
strokeColor=#3C7FC0;fontSize=12;arcSize=10;dashed=1;dashPattern=8 4;
verticalAlign=middle;align=center;spacing=6;
```

- Пунктирная рамка обозначает асинхронный компонент

### 1.7 Component

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=#85BBF0;fontColor=#000000;
strokeColor=#78A8D8;fontSize=11;arcSize=6;verticalAlign=middle;
align=center;spacing=4;
```

- **Размер**: 220–240 × 90 px
- **Цвет**: `#85BBF0` (светло-голубой)
- **Текст**: чёрный

### 1.8 System Boundary (Граница системы)

```text
rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#1168BD;
fontSize=16;fontStyle=3;fontColor=#1168BD;dashed=1;dashPattern=8 4;
verticalAlign=top;align=left;spacing=10;container=0;
```

- **Цвет рамки**: `#1168BD` (пунктир)
- Используется как фоновый прямоугольник, `container=0` для простоты

### 1.9 Связь (Relationship)

```text
html=1;fontSize=11;fontColor=#404040;strokeColor=#666666;strokeWidth=2;
endArrow=blockThin;endFill=1;edgeStyle=orthogonalEdgeStyle;curved=1;
rounded=1;
```

- **Ортогональная маршрутизация**: `edgeStyle=orthogonalEdgeStyle`
- **Скруглённые углы**: `curved=1;rounded=1`
- Подпись: назначение + протокол в квадратных скобках

## 2. Алгоритм размещения (Layout Algorithm)

### 2.1 Константы размещения

| Параметр | Значение | Описание |
| --- | --- | --- |
| `PERSON_W` | 200 | Ширина Person |
| `PERSON_H` | 180 | Высота Person |
| `SYSTEM_W` | 280–400 | Ширина Software System |
| `SYSTEM_H` | 180–200 | Высота Software System |
| `EXTERNAL_W` | 240 | Ширина External System |
| `EXTERNAL_H` | 160 | Высота External System |
| `CONTAINER_W` | 200 | Ширина Container |
| `CONTAINER_H` | 120 | Высота Container |
| `DB_W` | 200 | Ширина Database |
| `DB_H` | 90 | Высота Database |
| `COMPONENT_W` | 220 | Ширина Component |
| `COMPONENT_H` | 90 | Высота Component |
| `GAP_H` | 50–80 | Горизонтальный отступ между элементами |
| `GAP_V` | 60–80 | Вертикальный отступ между слоями |
| `BOUNDARY_PAD` | 40–60 | Отступ внутри boundary |

### 2.2 Иерархическое размещение (Top-to-Bottom)

Элементы распределяются по горизонтальным слоям (ranks).

#### Context Diagram (Level 1)

```text
Rank 0: Actors / Persons               — верх диаграммы
Rank 1: Target Software System          — центр
Rank 2: External Systems                — низ диаграммы
```

#### Container Diagram (Level 2)

```text
Rank 0: Actors / Persons
Rank 1: Frontend containers (SPA, Mobile)
Rank 2: Gateway / BFF
Rank 3: Application Services (доменные сервисы)
Rank 4: Data Stores (DB, Cache, Queue, Storage) — по сервисам
Rank 5: Shared Infrastructure (Redis, Kafka, S3) — общее
Rank 6: External Systems (PSP, IdP, Email)
```

#### Component Diagram (Level 3)

```text
Rank 0: Входящие связи (API Gateway / другие сервисы)
Rank 1: API Controllers / Handlers
Rank 2: Application Services / Use Cases
Rank 3: Infrastructure (Repositories, Publishers, Providers)
Rank 4: Data Stores (DB, Kafka, Redis)
```

### 2.3 Алгоритм расчёта координат

```text
function calculateLayout(ranks, canvasWidth):

  y = GAP_V                            // начальный отступ сверху

  for each rank in ranks:
    elements = rank.elements
    count = elements.length
    maxHeight = max(el.height for el in elements)

    // Общая ширина слоя
    totalWidth = sum(el.width for el in elements)
                 + (count - 1) * GAP_H

    // Центрирование слоя на канве
    startX = (canvasWidth - totalWidth) / 2

    // Расстановка элементов в слое
    x = startX
    for each el in elements:
      el.x = x
      el.y = y + (maxHeight - el.height) / 2   // вертикальное центрирование
      x += el.width + GAP_H

    y += maxHeight + GAP_V
```

### 2.4 Правила предотвращения пересечений

1. **Вертикальное выравнивание**: если элемент A в rank N связан
   с элементом B в rank N+1, по возможности размещать B
   непосредственно под A (совпадение по x).

2. **Барицентрическая эвристика**: если элемент A связан с несколькими
   элементами в следующем rank, размещать A над серединой
   (средним x) связанных элементов.

3. **Database-per-Service выравнивание**: каждый сервис → его data store
   размещается точно под сервисом. Это устраняет все пересечения
   в слое "сервисы → хранилища".

4. **Fan-out из центра**: элемент-маршрутизатор (API Gateway) размещается
   по центру, целевые элементы — симметрично слева и справа.
   Связи расходятся веером без пересечений.

5. **Порядок в слое определяется связями**: элементы, связанные
   с левыми элементами предыдущего слоя, размещаются левее.

6. **Вынос внешних систем**: элементы с единичной связью
   выносятся в отдельный ряд снизу или сбоку.

### 2.5 Правила маршрутизации соединений

1. **Ортогональная маршрутизация**: все связи используют
   `edgeStyle=orthogonalEdgeStyle` для прямоугольных путей.

2. **Скруглённые углы**: `curved=1;rounded=1` для визуальной мягкости.

3. **Top-to-Bottom flow**:
   - Выход: нижняя сторона элемента (по умолчанию)
   - Вход: верхняя сторона элемента (по умолчанию)

4. **Боковые связи**: для связей к внешним системам сбоку:
   - Явно задавать `exitX=0;exitY=0.5` (левая сторона)
   - Или `exitX=1;exitY=0.5` (правая сторона)

5. **Fan-out точки выхода**: при множественных связях из одного
   элемента распределять exitX по ширине элемента (0.1, 0.3, 0.5, 0.7, 0.9)
   для уменьшения скученности.

## 3. XML-шаблон draw.io

### 3.1 Базовая структура файла

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" type="device">
  <diagram name="{diagram_name}" id="{unique_id}">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10"
                  guides="1" tooltips="1" connect="1" arrows="1"
                  fold="1" page="1" pageScale="1"
                  pageWidth="{width}" pageHeight="{height}"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Элементы и связи -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 3.2 Шаблон элемента (vertex)

```xml
<mxCell id="{id}"
        value="{label_html_encoded}"
        style="{style_string}"
        vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
</mxCell>
```

### 3.3 Шаблон связи (edge)

```xml
<mxCell id="{id}"
        value="{label_html_encoded}"
        style="{edge_style}"
        edge="1" source="{source_id}" target="{target_id}" parent="1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### 3.4 Шаблон System Boundary

```xml
<mxCell id="{boundary_id}"
        value="{boundary_label}"
        style="{boundary_style}"
        vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
</mxCell>
```

Boundary размещается как фоновый элемент. Дочерние элементы
используют `parent="1"` (не `parent="{boundary_id}"`) для
абсолютного позиционирования, что упрощает расчёт координат.

## 4. HTML-разметка подписей (Labels)

Все подписи используют HTML-encoded формат в атрибуте `value`.

### Person

```text
&lt;b&gt;Покупатель&lt;/b&gt;&lt;br&gt;&lt;i&gt;[Person]&lt;/i&gt;&lt;br&gt;&lt;br&gt;Описание роли
```

### Software System

```text
&lt;b&gt;EBookStore&lt;/b&gt;&lt;br&gt;&lt;i&gt;[Software System]&lt;/i&gt;&lt;br&gt;&lt;br&gt;Описание системы
```

### Container

```text
&lt;b&gt;Catalog Service&lt;/b&gt;&lt;br&gt;&lt;i&gt;[Container: .NET 8]&lt;/i&gt;&lt;br&gt;&lt;br&gt;Описание
```

### Component

```text
&lt;b&gt;BookRepository&lt;/b&gt;&lt;br&gt;&lt;i&gt;[Component: Repository]&lt;/i&gt;&lt;br&gt;&lt;br&gt;Описание
```

### Связь

```text
Описание действия&lt;br&gt;[Протокол]
```

## 5. Пошаговый алгоритм генерации

1. **Определить уровень C4**: Context / Container / Component.
2. **Перечислить элементы** и их типы (Person, System, Container, и т.д.).
3. **Определить связи** между элементами (source, target, label, protocol).
4. **Распределить по ranks** (слоям) согласно правилам раздела 2.2.
5. **Оптимизировать порядок** в каждом rank:
   - Применить барицентрическую эвристику (2.4.2).
   - Для Container diagrams: database-per-service выравнивание (2.4.3).
6. **Вычислить размер канвы**:
   - `width` = максимальная ширина слоя + 2 × BOUNDARY_PAD.
   - `height` = сумма высот слоёв + gaps + отступы.
7. **Вычислить координаты** по алгоритму из раздела 2.3.
8. **Назначить стили** из раздела 1.
9. **Сгенерировать XML** по шаблонам из раздела 3.
10. **Верифицировать**:
    - Каждый элемент имеет уникальный `id`.
    - Все `source` / `target` в edges ссылаются на существующие id.
    - Нет перекрытий (для любых двух элементов в одном rank:
      `el1.x + el1.width + GAP_H <= el2.x`).
    - Boundary охватывает все внутренние элементы с padding.

## 6. Стратегии устранения типичных пересечений

### 6.1 Fan-out (один источник → много целей)

**Проблема**: API Gateway связан с 6 сервисами — связи пересекаются.

**Решение**: разместить Gateway по центру, сервисы симметрично
слева и справа. Связи расходятся веером.

```text
            [API Gateway]
         /   /   |   \   \
     [S1] [S2] [S3] [S4] [S5]
```

### 6.2 Fan-in (много источников → одна цель)

**Проблема**: несколько сервисов пишут в одну БД.

**Решения**:

- **Database-per-Service**: каждый сервис получает свой экземпляр БД,
  размещённый строго под ним. Нет пересечений.
- **Барицентр**: БД размещается под средним x всех связанных сервисов.
  Связи сходятся к одной точке, минимизируя пересечения.

### 6.3 Cross-layer связи (пропуск слоя)

**Проблема**: элемент из rank 1 связан с элементом в rank 3,
пропуская rank 2. Связь проходит через элементы rank 2.

**Решение**: использовать боковой маршрут — связь выходит
со стороны элемента, обходит промежуточный слой и входит
сверху в целевой элемент.

### 6.4 Двунаправленные связи

**Проблема**: сервис A вызывает сервис B и наоборот.

**Решение**: использовать одну связь с двойными стрелками
(`endArrow=blockThin;startArrow=blockThin;startFill=1;endFill=1`)
и подписью, описывающей оба направления.

## 7. Чек-лист качества диаграммы

- [ ] Все элементы имеют тип и описание в подписи
- [ ] Все связи подписаны (действие + протокол)
- [ ] Элементы не перекрываются (min GAP_H / GAP_V между любыми двумя)
- [ ] Связи не проходят через элементы (ортогональная маршрутизация)
- [ ] Цветовая схема соответствует стандарту C4
- [ ] System boundary обрамляет все внутренние элементы с padding
- [ ] XML валиден (корректные id, parent, source, target)
- [ ] Канва не содержит лишнего пустого пространства
- [ ] Подписи связей читаемы и не перекрывают элементы

## 8. Примеры

Готовые примеры для EBookStore:

| Файл | Уровень | Описание |
| --- | --- | --- |
| `src/diagrams/drawio/c4-context-ebookstore.drawio` | Context (L1) | Контекст системы: пользователи, EBookStore, внешние системы |
| `src/diagrams/drawio/c4-container-ebookstore.drawio` | Container (L2) | Контейнеры: SPA, Gateway, сервисы, хранилища |
| `src/diagrams/drawio/c4-component-catalog.drawio` | Component (L3) | Компоненты Catalog Service: controller, service, repos |

## История версий

### v1.0 (2026-02-09)

- Начальная версия skill для генерации C4 draw.io диаграмм.
- Полный набор стилей элементов C4.
- Алгоритм иерархического размещения.
- Правила предотвращения пересечений.
- Стратегии устранения типичных проблем.
- Три примера диаграмм для EBookStore.

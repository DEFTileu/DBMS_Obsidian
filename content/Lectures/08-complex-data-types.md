# 08 — Complex Data Types

> Зачем эта тема: реальные данные не всегда влезают в скалярные `INT`/`VARCHAR`. JSON, массивы, гео-точки, тип-наследование — всё это **усложнённые типы**, которые добавили в SQL/OR-СУБД. На финале спрашивают про JSON и semi-structured data, плюс отличия object-relational.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/29

---

## 1. Зачем сложные типы

Чистая реляционная модель требует атомарности (1NF). Но в жизни:
- API возвращает **JSON** — хочется хранить как есть, а не размазывать по 5 таблицам.
- У точки на карте есть `(latitude, longitude)` — это **composite**.
- У продукта список **тегов** — это естественно массив.
- У сотрудника может быть **подкласс** (Manager, Engineer) — это object-relational.

DBMS подкручивает реляционную модель и добавляет:
- semi-structured (JSON/XML),
- arrays / multisets,
- composite types,
- inheritance (object-relational),
- temporal & spatial типы.

> [!abstract] Главная идея
> SQL давно вышел за рамки 1NF. Современная реляционная СУБД — это **гибрид** реляционной модели + объектно-ориентированных и документ-ориентированных возможностей.

---

## 2. Semi-structured data (JSON/XML)

**semi-structured** — данные с гибкой схемой: каждая запись может иметь свой набор полей. #dbterm

### 2.1 JSON

В Postgres есть два типа:
- `JSON` — хранит как текст, проверяет валидность.
- `JSONB` — хранит в бинарном формате, **рекомендуется** (быстрее запросы, поддержка индексов).

```sql
CREATE TABLE products (
    id   INT PRIMARY KEY,
    name VARCHAR(100),
    info JSONB
);

INSERT INTO products VALUES
    (1, 'Laptop', '{"cpu":"i7","ram":16,"tags":["new","sale"]}'),
    (2, 'Phone',  '{"cpu":"A17","ram":8,"tags":["premium"]}');
```

### 2.2 Доступ к JSON

Postgres операторы:
| Оператор | Что делает |
|---|---|
| `->` | вернуть JSON-поле (как JSON) |
| `->>` | вернуть как текст |
| `#>` | путь до элемента (массив ключей) |
| `#>>` | путь, как текст |
| `@>` | "содержит" (containment) |
| `?` | проверка существования ключа |

```sql
SELECT name, info->>'cpu' AS cpu
FROM products
WHERE info->>'ram' = '16';

-- Поиск по containment
SELECT name FROM products WHERE info @> '{"tags":["sale"]}';

-- Существует ли ключ
SELECT name FROM products WHERE info ? 'cpu';
```

`->>` #sqlcommand — извлекает значение JSON-поля как текст.

`@>` #sqlcommand — JSONB containment.

### 2.3 Индексы по JSON

```sql
CREATE INDEX idx_products_info ON products USING GIN (info);
```

GIN-индекс ускоряет `@>` и `?` запросы.

### 2.4 XML

Стандарт SQL поддерживает `XML` тип и **XQuery** / `XMLEXISTS`. На практике сейчас вытесняется JSON — упоминается на финале, но реже встречается.

> [!tip] JSON vs нормализация
> JSON хорош, когда:
> - данные приходят как документ от внешней системы;
> - схема может меняться;
> - запросы по содержимому редкие или специфичные.
>
> Нормализация лучше, когда:
> - данные регулярные и структурированные;
> - часто JOIN-ишь с другими таблицами.

> [!warning] Не клади всё в JSON
> "Просто положу всё в JSON" → теряешь выгоды реляционной модели: FK, нормализацию, типы, оптимизатор. JSON — для документной части, реляционные таблицы — для связей.

---

## 3. Arrays

В Postgres любой тип может быть массивом.

```sql
CREATE TABLE employees (
    id     INT PRIMARY KEY,
    name   VARCHAR(100),
    skills TEXT[]
);

INSERT INTO employees VALUES (1, 'Aigerim', ARRAY['SQL','Python','Docker']);
```

Запросы:
```sql
SELECT name FROM employees WHERE 'SQL' = ANY(skills);
SELECT name FROM employees WHERE skills @> ARRAY['SQL','Python'];

-- Развернуть массив в строки
SELECT name, unnest(skills) AS skill FROM employees;
```

`ANY(array)` #sqlcommand — проверка вхождения.

`unnest(array)` #sqlcommand — разворачивает массив в строки.

> [!warning] Массивы и нормализация
> Массивы нарушают 1NF. На практике — иногда удобно для тегов и небольших фиксированных списков. Для больших или часто меняющихся коллекций лучше отдельная таблица.

---

## 4. Composite (User-defined) types

Пользовательский тип = "структура" с несколькими полями.

```sql
CREATE TYPE address_t AS (
    street  VARCHAR(100),
    city    VARCHAR(50),
    zip     VARCHAR(10)
);

CREATE TABLE customers (
    id   INT PRIMARY KEY,
    name VARCHAR(100),
    addr address_t
);

INSERT INTO customers VALUES (1, 'Aigerim', ROW('Abay 10','Almaty','050000'));
SELECT name, (addr).city FROM customers;
```

`CREATE TYPE name AS (…)` #sqlcommand — создаёт composite тип.

> [!tip] Composite vs JSON
> Composite — типизирован, через DDL. JSON — гибче, без проверки структуры. Composite полезен, когда поля стабильны и нужны type-checks.

---

## 5. Object-Relational Database (ORDBMS)

**ORDBMS** — реляционная СУБД с объектно-ориентированными расширениями: composite types, inheritance, references. #abbreviation
**ODBMS** — чисто объектная, без таблиц (редко в индустрии).

### 5.1 Inheritance таблиц (Postgres)

```sql
CREATE TABLE persons (
    id   INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    salary DECIMAL(15,2)
) INHERITS (persons);

INSERT INTO employees(id, name, salary) VALUES (1, 'Aigerim', 500000);

SELECT * FROM persons;       -- увидит и сотрудников
SELECT * FROM ONLY persons;  -- только без потомков
```

> [!warning] PG inheritance — не магия
> FK и UNIQUE не наследуются автоматически. На практике используется редко; чаще предпочитают ISA-перевод в нормальные таблицы.

### 5.2 Methods

В стандарте SQL у типов могут быть **методы** (как в ООП). На практике в Postgres методы обычно реализуются как функции `function(type)`.

---

## 6. Temporal data — даты, время, интервалы

| Тип | Хранит |
|---|---|
| `DATE` | дата (без времени) |
| `TIME` | время дня |
| `TIMESTAMP` | дата+время |
| `TIMESTAMP WITH TIME ZONE` | + часовой пояс |
| `INTERVAL` | продолжительность |

```sql
SELECT NOW() - INTERVAL '7 days';
SELECT EXTRACT(YEAR FROM birth_date) FROM customers;
SELECT AGE(birth_date) FROM customers;
SELECT NOW() AT TIME ZONE 'Asia/Almaty';
```

`NOW()` #sqlcommand — текущая метка времени.

`EXTRACT(part FROM ts)` #sqlcommand — выделяет часть даты/времени.

`INTERVAL 'n unit'` #sqlcommand — продолжительность.

`AT TIME ZONE 'tz'` #sqlcommand — конвертация в часовой пояс.

### 6.1 Temporal queries

"Активные подписки на дату":
```sql
SELECT * FROM subscriptions
WHERE start_date <= '2026-05-01' AND end_date > '2026-05-01';
```

"Перекрытие интервалов":
```sql
WHERE NOT (a.end < b.start OR a.start > b.end)
```

> [!important] TIMESTAMP WITH/WITHOUT TIME ZONE
> Для прода почти всегда нужен `TIMESTAMP WITH TIME ZONE` (хранится в UTC, конвертируется при чтении). Без TZ — источник багов с переходом на летнее время.

### 6.2 Bitemporal / valid time

Иногда нужно знать, **когда** факт был истинным (valid time) и **когда** он был записан (transaction time). Это bitemporal модель — тяжёлая, не часто на финале.

---

## 7. Spatial data — гео

PostGIS — расширение Postgres для работы с гео-объектами.

```sql
CREATE EXTENSION postgis;

CREATE TABLE places (
    id   INT PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(POINT, 4326)
);

INSERT INTO places VALUES (1, 'SDU', ST_SetSRID(ST_MakePoint(76.928, 43.222), 4326));

-- Найти всё в радиусе 1 км от точки
SELECT name FROM places
WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(76.93, 43.22), 4326), 1000);
```

`POINT`, `LINESTRING`, `POLYGON`, `MULTIPOLYGON` — типы геометрий.
**SRID** (Spatial Reference ID) — система координат (4326 = WGS84). #abbreviation

> [!tip] Spatial индексы
> `CREATE INDEX … USING GIST (geom);` — обязательно при больших объёмах. Без индекса гео-запросы — full scan.

---

## 8. LOB — Large Objects

| Тип | Что хранит |
|---|---|
| `BLOB` / `BYTEA` | бинарные данные (картинки, файлы) |
| `CLOB` / `TEXT` | большие текстовые данные |

> [!warning] Картинки в БД?
> Технически можно. На практике **обычно нет**: bloat-ит БД, бэкапы становятся гигантскими. Лучше хранить файлы в object storage (S3) и в БД — только URL.

---

## 9. ENUM — перечисления

```sql
CREATE TYPE account_type AS ENUM ('checking', 'savings', 'loan');

CREATE TABLE accounts (
    id   INT PRIMARY KEY,
    type account_type
);
```

Жёсткий контроль допустимых значений. Альтернатива — `CHECK (type IN ('…'))` или отдельная reference-таблица.

> [!tip] ENUM vs reference table
> ENUM проще. Reference-таблица гибче (можно добавлять без `ALTER TYPE`). На практике оба варианта живы.

---

## 10. Range types (Postgres)

```sql
CREATE TABLE bookings (
    room_id  INT,
    period   tstzrange
);

INSERT INTO bookings VALUES (1, '[2026-05-10 10:00, 2026-05-10 12:00)');

-- Пересечение
SELECT * FROM bookings WHERE period && '[2026-05-10 11:00, 2026-05-10 13:00)';
```

`tstzrange`, `daterange`, `int4range` — встроенные range-типы.
`&&` — пересечение интервалов.

> [!tip] Замена двух колонок start_at/end_at
> Range-тип + `EXCLUDE USING gist (room_id WITH =, period WITH &&)` — гарантирует, что не будет двух пересекающихся бронирований.

---

## 11. UUID

```sql
CREATE EXTENSION "uuid-ossp";

CREATE TABLE events (
    id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    body TEXT
);
```

UUID — глобально уникальный идентификатор, удобен в распределённых системах (не нужно центрального счётчика).

> [!warning] UUID как PK — нюансы
> Случайный UUID плохо ложится на B-tree (вставки рассеяны → fragmentation). Современные UUIDv7 / ULID решают это (упорядочены по времени).

---

## 12. Semi-structured paradigms — обзор

| Парадигма | Пример хранения | Когда |
|---|---|---|
| **Document** | JSON в Postgres / MongoDB | гибкая схема, иерархия |
| **Key-value** | Redis | кеш, простые маппинги |
| **Wide-column** | Cassandra | очень большие распределённые БД |
| **Graph** | Neo4j, AGE | связи, рекомендации, соцсети |

> [!tip] PolyDB / Multi-model
> Современный Postgres = реляционный + JSON + key-value (через extensions) + graph (AGE) + time-series (Timescale). Часто это лучше, чем жонглировать пятью разными СУБД.

---

## 13. Часто на экзамене

> [!danger] Exam traps
> 1. **JSON vs JSONB** — JSONB бинарный, рекомендуется.
> 2. **JSON и 1NF** — формально нарушает атомарность.
> 3. **TIMESTAMP с TZ vs без** — для прода нужен с TZ.
> 4. **ORDBMS vs ODBMS** — OR это реляционная + объектные расширения, OD это чисто объектная.
> 5. **Range types + EXCLUDE constraint** — для бронирований.
> 6. **GIN индекс для JSON/массивов**, GiST для гео.

---

## 14. Mini-quiz

1. Чем отличается `JSON` от `JSONB`?
2. Почему `JSON` формально нарушает 1NF?
3. Что вернёт `info->>'ram'` если `info` это `JSONB`?
4. Какой индекс нужен для быстрого `info @> '{"tag":"x"}'`?
5. Зачем хранить `TIMESTAMP WITH TIME ZONE` вместо обычного?

> [!success] Если понял эту главу
> Ты знаешь, как современный Postgres работает с JSON, массивами, временем, гео-данными, и понимаешь, когда выходить из реляционной чистоты, а когда — оставаться в нормализованной модели.
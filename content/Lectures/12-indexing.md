# 12 — Indexing

> Зачем эта тема: **индексы — это то, что делает БД быстрой**. На финале гарантированно: тип индексов, B+ tree, hash index, clustered vs non-clustered, плюсы и минусы. Без этой главы все запросы — это full scan.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/33

---

## 1. Зачем индекс

Без индекса:
```
SELECT * FROM customers WHERE email = 'a@x.com';
→ full table scan: прочитать ВСЕ строки → 1M строк → 10 секунд.
```

С индексом по email:
```
→ B+ tree lookup → 3-4 disk reads → 10 ms.
```

> [!abstract] Главная идея
> Индекс — это **отдельная структура данных**, которая позволяет быстро находить записи без чтения всей таблицы. Цена — место на диске и замедление INSERT/UPDATE/DELETE.

**index** — структура `key → location`, ускоряющая поиск по ключу. #dbterm

**search key** — атрибут (или их комбинация), по которому строится индекс. #dbterm

---

## 2. Виды индексов — сводка

| По структуре | По свойствам | По применению |
|---|---|---|
| B+ tree | Clustered | Primary |
| Hash | Non-clustered | Secondary |
| Bitmap | Unique | Composite |
| GIN, GiST | Sparse | Covering |
| Bloom | Partial | Functional |

---

## 3. Dense vs Sparse index

**Dense index** — указатель на КАЖДУЮ запись.
**Sparse index** — указатель только на каждую N-ю (например, на первую запись каждого блока).

```
Dense:                 Sparse:
key1 → row1            key1  → block 1 (где лежат rows 1-5)
key2 → row2            key6  → block 2
key3 → row3            key11 → block 3
key4 → row4
...
```

> [!tip] Sparse требует sortedness
> Sparse имеет смысл только над **отсортированной** таблицей (sequential file). В heap-файле — только dense.

---

## 4. Primary vs Secondary index

**Primary index** — по primary key, сама таблица отсортирована по этому ключу (cluster). #dbterm

**Secondary index** — по любому другому атрибуту, таблица не отсортирована по нему. #dbterm

В Postgres:
- Все индексы технически secondary (heap файл).
- Cluster — это команда `CLUSTER tbl USING idx`, которая физически сортирует таблицу. Со временем сортировка распадается.

В MySQL InnoDB:
- Primary key — это **clustered index**, сама таблица = B+ tree по PK.
- Все остальные — secondary; листья хранят PK, а не RID.

---

## 5. B+ tree — главный индекс

**B+ tree** — сбалансированное многоуровневое дерево, основа большинства индексов в реляционных СУБД. #dbterm

### 5.1 Структура

```
              [50, 100]                   ← root
             /    |     \
        [10,30] [70,80]  [120,150]        ← internal nodes
        / | \    /|\       /|\
      ↓                              ↓
    [leaves: sorted keys + RIDs] ← linked list
```

- Внутренние узлы: ключи + указатели на дочерние узлы.
- Листья: ключи + указатели на записи (RID), связаны в **двусвязный список**.

### 5.2 Свойства

- **Сбалансированное** — высота O(log_b N), где b — fanout.
- **Высокий fanout** (~100-1000 ключей в узле) → дерево очень "плоское".
- **Range scan** — переход по leaf list влево/вправо.

### 5.3 Поиск

Точечный (`=`):
1. От root: спускаться по нужной ветке.
2. На листе: найти точный ключ → RID → запись.
3. ~3-4 disk read для миллионов строк.

Range (`BETWEEN`, `>`, `<`):
1. Найти левую границу.
2. Идти по leaf list вправо до правой границы.

```sql
SELECT * FROM customers WHERE balance BETWEEN 1000 AND 5000;
-- Использует индекс: найти 1000 → идти по листьям вправо до 5000.
```

### 5.4 INSERT

1. Найти лист.
2. Если место есть — вставить.
3. Если переполнение — **split**: разделить лист пополам, продвинуть средний ключ в родителя.
4. Если родитель переполнен — split рекурсивно вверх.

### 5.5 DELETE

1. Найти лист, удалить.
2. Если узел "пустеет" — заём у соседа или **merge**.
3. Иногда оставляют слегка недополненные узлы (lazy delete).

### 5.6 Почему B+ а не B

В классическом **B-tree** значения хранятся и в листьях, и во внутренних узлах. В **B+ tree** — только в листьях. Преимущества B+:
- Внутренние узлы компактнее → fanout выше → дерево ниже.
- Листья связаны → range scan быстрый.

> [!important] B+ tree — стандарт
> Если в задаче не сказано иначе — индекс B+ tree.

---

## 6. Hash index

Хеш-функция от ключа → bucket (страница). Поиск точечного значения — O(1).

| | B+ tree | Hash |
|---|---|---|
| Точечный поиск (`=`) | O(log N) | O(1) |
| Range scan | да | нет |
| Sorted output | да | нет |
| Подходит для PK | да | да (если только `=`) |

> [!warning] Hash не для range
> `WHERE x BETWEEN a AND b` хеш не помогает — данные разбросаны по всем bucket-ам.

### 6.1 Static vs Dynamic hashing

- **Static** — фиксированное число buckets. Если данных больше — overflow chains, медленно.
- **Linear hashing**, **Extendible hashing** — динамически расширяются.

В PostgreSQL hash-индексы есть, но используются редко — B+ tree почти всегда не хуже.

---

## 7. Bitmap index

Для каждого значения атрибута — битовая карта: 1 если строка имеет это значение, 0 если нет.

```
status = 'OK':   1 0 1 1 0 1 0 1
status = 'FAIL': 0 1 0 0 1 0 1 0
```

Хорошо когда:
- Кардинальность низкая (мало уникальных значений: пол, статус).
- Много операций AND/OR между условиями.

```sql
WHERE gender = 'M' AND status = 'active'
→ AND двух bitmap → результат за миллисекунды.
```

> [!warning] Не для OLTP
> Bitmap-индексы плохо обновляются (нужно править bit во многих местах). Используются в OLAP/data warehouse.

---

## 8. Specialized indexes

### 8.1 GIN (Generalized Inverted Index)

Для составных значений: массивы, JSONB, полнотекстовый поиск.

```sql
CREATE INDEX idx_tags ON products USING GIN (tags);
CREATE INDEX idx_info ON products USING GIN (info jsonb_path_ops);
```

### 8.2 GiST (Generalized Search Tree)

Для геометрии, range types, full-text.

```sql
CREATE INDEX idx_geom ON places USING GIST (geom);
```

### 8.3 BRIN (Block Range INdex)

Для очень больших таблиц с естественным порядком (например, time-series). Хранит min/max по блоку. Очень компактный, не очень точный.

### 8.4 Bloom

Probabilistic. Позволяет быстро сказать "точно нет" или "возможно есть". Используется для проверки существования с малыми ложноположительными.

---

## 9. Composite (multi-column) index

Индекс по нескольким столбцам, в указанном порядке.

```sql
CREATE INDEX idx_a_b_c ON t(a, b, c);
```

### 9.1 Когда работает

- `WHERE a = …` ✅ работает.
- `WHERE a = … AND b = …` ✅ работает.
- `WHERE a = … AND b = … AND c = …` ✅ работает.
- `WHERE a = … AND c = …` ⚠️ частично (только `a`).
- `WHERE b = …` ❌ не работает.

> [!important] Left-prefix rule
> Composite индекс используется только если префикс (первые столбцы) использован в `WHERE`. Думай как о телефонной книге: фамилия → имя → отчество.

### 9.2 Порядок столбцов

Кладите наиболее селективный (различимый) первым? Не всегда. Главное — фильтрация по первому. Если запросы только `(a, b)` — порядок `(a, b)` подойдёт.

---

## 10. Covering index

Индекс, в котором есть ВСЕ столбцы, нужные запросу. DBMS читает только индекс, не лезет в таблицу.

```sql
CREATE INDEX idx_email_name ON customers(email) INCLUDE (name);

SELECT name FROM customers WHERE email = 'a@x.com';
-- index-only scan → не читать heap.
```

`INCLUDE (cols)` (Postgres 11+) — добавляет столбцы в leaf, без участия в порядке.

> [!tip] Index-only scan
> Самый быстрый вид доступа. Достигается через covering index + visibility map (Postgres).

---

## 11. Partial index

Индекс только по подмножеству строк.

```sql
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
```

Меньше места, быстрее обновление, работает только для запросов с тем же условием.

---

## 12. Functional / expression index

Индекс по результату выражения.

```sql
CREATE INDEX idx_lower_email ON customers(LOWER(email));

SELECT * FROM customers WHERE LOWER(email) = 'a@x.com';
```

> [!warning] WHERE должен совпадать
> Если индекс по `LOWER(email)`, а в запросе `email`, индекс не используется. Запрос должен повторять выражение.

---

## 13. Unique vs Non-unique index

```sql
CREATE UNIQUE INDEX idx_email ON customers(email);
```

- **UNIQUE** — гарантирует уникальность + ускоряет lookup.
- Создаётся автоматически для `PRIMARY KEY` и `UNIQUE` constraint.

---

## 14. Cost of indexes

| Что замедляется | Почему |
|---|---|
| INSERT | надо вставить и в таблицу, и в каждый индекс |
| UPDATE | если меняется индексированный столбец — пересчёт |
| DELETE | удаление из всех индексов |
| Disk space | каждый индекс — свои страницы |

> [!warning] Слишком много индексов
> Каждый индекс — налог на запись. Если на таблице 15 индексов, INSERT медленнее в разы. Создавай индексы по реальным запросам, не "на всякий случай".

> [!important] Правило 3-5 индексов
> Для типичной OLTP-таблицы — 3-5 индексов хватает. Больше — повод пересмотреть схему.

---

## 15. Когда индекс НЕ помогает

- Запрос возвращает большую долю таблицы (>20-30%) — full scan дешевле.
- Маленькие таблицы (<10 страниц) — full scan быстрее.
- Селективность плохая (`WHERE gender = 'M'` — половина таблицы).
- Условие нельзя свести к индексу (`WHERE LOWER(name) = …` без functional index).
- В операторе функция от столбца (`WHERE date_trunc('month', d) = …`).

> [!tip] EXPLAIN — твой друг
> `EXPLAIN ANALYZE SELECT …` показывает, использует ли запрос индекс или делает Seq Scan.

---

## 16. Создание индекса в SQL

```sql
-- Простой
CREATE INDEX idx_email ON customers(email);

-- Уникальный
CREATE UNIQUE INDEX idx_passport ON customers(passport_no);

-- Composite
CREATE INDEX idx_city_balance ON customers(city, balance DESC);

-- Partial
CREATE INDEX idx_active ON customers(email) WHERE active = TRUE;

-- Functional
CREATE INDEX idx_lower_email ON customers(LOWER(email));

-- Specific access method (Postgres)
CREATE INDEX idx_tags ON products USING GIN (tags);
CREATE INDEX idx_geom ON places USING GIST (geom);

-- Удаление
DROP INDEX idx_email;
```

`CREATE INDEX name ON table(col);` #sqlcommand — создаёт индекс.

`CREATE UNIQUE INDEX …` #sqlcommand — индекс с уникальностью.

`USING GIN/GIST/BTREE/HASH` #sqlcommand — выбор метода доступа.

> [!tip] CREATE INDEX CONCURRENTLY (Postgres)
> На production-таблицах используй `CONCURRENTLY` — индекс строится без блокировки записи. Долго, но без downtime.

---

## 17. Sparse vs Dense — пример

Таблица отсортирована по `id`:
```
Block 1: id=1, id=2, id=3
Block 2: id=4, id=5, id=6
Block 3: id=7, id=8, id=9
```

**Dense index:**
| key | RID |
|---|---|
| 1 | (B1,1) |
| 2 | (B1,2) |
| 3 | (B1,3) |
| 4 | (B2,1) |
| ... | ... |

**Sparse index:**
| key | block |
|---|---|
| 1 | B1 |
| 4 | B2 |
| 7 | B3 |

Для поиска `id=5`: sparse → найти блок (4 ≤ 5 < 7 → B2) → читать блок → найти 5.

---

## 18. Часто на экзамене

> [!danger] Exam traps
> 1. **B+ tree высота** = O(log_b N), где b — fanout.
> 2. **Hash vs B+ tree** — hash не для range.
> 3. **Clustered vs non-clustered** — таблица отсортирована или нет.
> 4. **Composite index left-prefix rule** — нужен первый столбец в WHERE.
> 5. **INSERT медленнее с индексами** — каждый индекс обновляется.
> 6. **Sparse требует sorted file**.
> 7. **Bitmap для low-cardinality** OLAP.
> 8. **Index-only scan / covering** — чтение без heap.

---

## 19. Mini-quiz

1. Какая высота B+ tree с fanout 100 для миллиарда записей?
2. Будет ли индекс на `(city, balance)` использоваться в `WHERE balance > 1000`?
3. Почему hash-индекс не подходит для `BETWEEN`?
4. В чём разница clustered и non-clustered с точки зрения хранения данных?
5. Когда полезен partial index?

> [!success] Если понял эту главу
> Ты понимаешь, как DBMS быстро находит данные, можешь выбрать правильный тип индекса под запрос, и знаешь цену каждого индекса. Это самое практичное знание из курса DBMS.
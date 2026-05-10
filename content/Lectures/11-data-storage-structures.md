# 11 — Data Storage Structures

> Зачем эта тема: **как DBMS укладывает таблицу на диск**. Как устроена страница, как пишется запись, как буфер-менеджер решает, какие блоки держать в памяти. Знание этого — ключ к пониманию индексов и query planner.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/32

---

## 1. Иерархия storage

```
Database  →  Tablespace  →  File  →  Page (block)  →  Record (row)
```

| Уровень | Что |
|---|---|
| **Database** | вся БД |
| **Tablespace** | логическая группа файлов |
| **File** | один или несколько файлов на диске |
| **Page (block)** | минимальная единица IO (4-16 KB) |
| **Record (row)** | одна строка таблицы |

**page** — фиксированный блок данных, минимальная единица чтения/записи в DBMS. #dbterm

**record** — представление одной строки таблицы внутри страницы. #dbterm

**tablespace** — логическая область, объединяющая несколько файлов хранения. #dbterm

---

## 2. File organization — как раскладывать строки в файл

### 2.1 Heap (unordered) file

Строки кладутся **куда есть место**. Без порядка.

- INSERT — быстро (в первое свободное место).
- Поиск без индекса — full scan.
- Стандарт для большинства таблиц + индексы.

### 2.2 Sequential file

Строки отсортированы по **search key** (например, `customer_id`).

- Поиск по ключу — быстро (binary search).
- INSERT — медленно: нужно вставлять "в середину" → сдвигать или использовать overflow chain.
- Применяется редко в чистом виде; B+ tree даёт похожие свойства лучше.

### 2.3 Hashing file

Хеш от ключа определяет страницу.

- Точечный поиск (`=`) — O(1).
- Range scan — нет.
- Используется для определённых индексов и для partitioning.

### 2.4 Clustering file (multitable clustering)

В одной странице хранятся **связанные** строки разных таблиц:
```
Page 1: department_10 + employees of dept 10
Page 2: department_20 + employees of dept 20
```

- JOIN таких таблиц — без отдельного IO.
- INSERT/UPDATE сложнее, страница может переполниться.
- Используется в Oracle (cluster), реже в Postgres.

> [!important] Heap по умолчанию
> В Postgres каждая таблица — heap. Сортировка/кластеризация — через `CLUSTER` команду + индекс, и со временем "размывается" обратно.

---

## 3. Page (block) layout

Страница — это структурированный кусок памяти/диска.

### 3.1 Slotted page (стандарт)

```
+------+----------------+--------+
|Header|      Free      |slot dir|
+------+----------------+--------+
| rec3 | rec2 |  rec1                ← растут с конца
| ........................................|
| → free space ...                          |
| ........................................|
| ← slot offsets growing from start         |
+--------------------------------------+
```

- **Header**: метаданные (free space, lsn, checksum).
- **Slot directory** в начале: массив offset-ов на записи.
- **Записи** растут с конца страницы.

> [!tip] Зачем slotted layout
> Записи имеют **переменную длину** (`VARCHAR`!). Если бы хранили подряд, удаление одной — сдвиг всех. Slot directory даёт стабильные **logical** ID (`(page_id, slot_no)`), а записи можно перемещать внутри страницы.

### 3.2 RID (Record ID)

**RID** = `(page_id, slot_no)` — физический адрес записи. #abbreviation

Индексы хранят `key → RID`. Перемещение записи в пределах страницы НЕ ломает RID, перемещение между страницами — ломает (DBMS перенаправляет через "tombstone" / TID forward).

---

## 4. Record formats

### 4.1 Fixed-length

Все строки одного размера. Просто, быстро. Подходит, когда нет `VARCHAR`/`TEXT`.

### 4.2 Variable-length

Реальность. Нужно хранить:
- длины полей или offset-ы,
- NULL bitmap,
- иногда указатель на overflow (TOAST) для очень больших значений.

```
[Header][Null bitmap][col1][col2 offset][col3 offset]...[col1 data][col2 data][col3 data]
```

### 4.3 NULL bitmap

Битовая маска: 1 = NULL, 0 = значение есть. Без неё пришлось бы выделять место под NULL.

### 4.4 TOAST (Postgres)

Для очень больших значений (> ~2 KB) Postgres хранит данные **отдельно** (compressed/out-of-line). Имя: TOAST = The Oversized Attribute Storage Technique.

> [!tip] TOAST = прозрачное сжатие+вынос
> Большие `TEXT`/`JSONB` автоматически попадают в TOAST. Это позволяет эффективно работать со страницами фиксированного размера.

---

## 5. Buffer manager

**buffer pool** — область в RAM, где DBMS держит копии страниц с диска. Без него — каждый запрос лез бы на диск. #dbterm

### 5.1 Алгоритм работы

```
Запрос на page P:
1. P в buffer pool? → отдать (cache hit)
2. Нет (cache miss):
   a. Найти свободный slot.
   b. Если все заняты — выбрать жертву (replacement policy).
   c. Если жертва "грязная" (dirty) — записать на диск.
   d. Прочитать P с диска в этот slot.
   e. Отдать.
```

### 5.2 Pin / Unpin

Когда query держит page для обработки — `pin`. Buffer manager не выбросит pinned страницу.
После обработки — `unpin`.

### 5.3 Dirty bit

Флаг "страница изменена, надо записать обратно на диск".

### 5.4 Replacement policies

Какую страницу выкинуть, когда нужно место?

| Policy | Идея |
|---|---|
| **LRU (Least Recently Used)** | выкидывать ту, что давно не трогали |
| **MRU (Most Recently Used)** | выкидывать только что использованную |
| **LFU** | выкидывать самую редко используемую |
| **Clock** | приближённый LRU, дешевле |
| **2Q / ARC / LIRS** | продвинутые комбинации |

LRU — стандарт.

> [!warning] LRU и full scan
> Один большой full scan загрузит миллионы страниц и вытеснит из cache "горячие" данные другого workload. Решение — отдельная политика для sequential scan (Postgres использует "ring buffer" для больших sequential).

### 5.5 Dirty page flush

Грязные страницы периодически записываются на диск:
- При выкидывании жертвы.
- По расписанию (background writer).
- При **checkpoint** (см. ch14).

> [!important] Checkpoint
> Точка, в которой DBMS гарантирует: все grязные страницы до этого момента сброшены на диск. Используется для recovery — при crash, восстанавливаемся с последнего checkpoint, не с начала времён.

---

## 6. Buffering и locality

### 6.1 Spatial locality

Если запросили page P, скорее всего скоро понадобится P+1 (sequential scan). DBMS делает **read-ahead** / **prefetch** — заранее подкачивает соседние страницы.

### 6.2 Temporal locality

Только что использованная страница, скорее всего, будет нужна снова. На этом стоит LRU.

> [!tip] Buffer hit ratio
> Метрика: процент запросов страниц, удовлетворённых из buffer pool. >99% — отлично, <90% — мало RAM или плохие запросы.

---

## 7. Tuple lifecycle

### 7.1 INSERT

1. Найти страницу со свободным местом.
2. Записать tuple (header + data).
3. Если страница в buffer — пометить dirty.
4. Записать в WAL (write-ahead log).
5. WAL flush → COMMIT.

### 7.2 UPDATE

Зависит от MVCC модели:

**In-place update** (MySQL InnoDB):
- Если новая запись помещается на той же странице — записать поверх.
- Если нет — переместить, оставить TID forward.

**Append-only / MVCC** (Postgres):
- Старая версия помечается как "deleted" (но остаётся для других транзакций).
- Новая версия добавляется в конец (или в свободное место).
- Vacuum потом убирает "мёртвые" версии.

> [!warning] Postgres VACUUM
> Из-за MVCC после массовых UPDATE/DELETE остаются "мёртвые" tuple. `VACUUM` помечает их свободными, `VACUUM FULL` физически уплотняет таблицу. Без vacuum таблица распухает.

### 7.3 DELETE

Похоже на UPDATE, физически часто только пометка "removed". Vacuum чистит позже.

---

## 8. MVCC — Multi-Version Concurrency Control

**MVCC** — каждая транзакция видит "снимок" данных на момент её начала. Старые версии хранятся, пока их видят активные транзакции. #abbreviation

Плюс:
- Чтение не блокирует запись и наоборот.

Минус:
- Bloat — нужно vacuum/garbage collection.

> [!tip] MVCC по умолчанию в современных СУБД
> Postgres, Oracle, SQL Server (snapshot isolation). MySQL InnoDB — да. SQLite — упрощённая версия.

---

## 9. Файлы Postgres

Каждая таблица = файл `base/<db_oid>/<rel_filenode>`. Размер файла ограничен (обычно 1 GB), большие таблицы разбиваются на сегменты.

Помимо данных:
- `_fsm` — Free Space Map (где есть место).
- `_vm` — Visibility Map (какие страницы "all-visible" — оптимизация vacuum).
- `pg_xlog` / `pg_wal` — WAL.

---

## 10. Compression

Современные DBMS умеют сжимать:
- **Page compression** — страница сжимается перед записью на диск (часто используется в SQL Server).
- **Column compression** — особенно эффективно в columnar storage (Parquet, ClickHouse).
- **Dictionary encoding** для повторяющихся значений.

> [!tip] Где compression хорошо
> На колоночных хранилищах для аналитики — экономия 5-20×. На OLTP с короткими строками — выигрыш меньше, оверхед больше.

---

## 11. Row-store vs Column-store

| | Row-store | Column-store |
|---|---|---|
| Раскладка | строка целиком в одном месте | столбец целиком |
| Workload | OLTP (чтение/запись отдельных строк) | OLAP (агрегаты по столбцам) |
| Compression | средне | очень хорошо |
| Примеры | Postgres, MySQL, Oracle | ClickHouse, Vertica, Parquet |

> [!important] Гибрид
> Современные СУБД часто гибридные: основная таблица row-store + columnar index/replica для аналитики (Oracle In-Memory, SQL Server columnstore index).

---

## 12. Часто на экзамене

> [!danger] Exam traps
> 1. **Slotted page** — записи растут с конца, slot directory с начала.
> 2. **Variable-length record** — нужны offset-ы и NULL bitmap.
> 3. **RID = (page, slot)** — стабильно при перемещениях внутри страницы.
> 4. **Buffer manager** — pin/unpin, dirty bit, LRU.
> 5. **Heap vs sequential vs hash file** — отличия.
> 6. **Clustering** — несколько связанных таблиц на одной странице.
> 7. **Row vs column store** — где какой workload.

---

## 13. Mini-quiz

1. Зачем slotted page хранит slot directory отдельно от данных?
2. Что произойдёт, если страница в buffer pool помечена dirty, и её вытесняют?
3. Чем heap file отличается от sequential file?
4. Почему MVCC требует vacuum?
5. Какой файл-формат лучше для аналитики: row-store или column-store?

> [!success] Если понял эту главу
> Ты знаешь, как таблица физически устроена в файлах, как страница хранит записи переменной длины, как buffer manager экономит обращения к диску. Это база для понимания индексов в следующей главе.
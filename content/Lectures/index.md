# Lectures Index — INF202 Database Management Systems

Учебные конспекты по курсу **DBMS (INF202)** — для подготовки к финалу.
Базируются на *Database System Concepts, 7th Ed.* — Silberschatz, Korth, Sudarshan.

> [!abstract] Зачем этот индекс
> Это карта всего курса. Открыл индекс → увидел тему → перешёл к нужной главе. Каждая глава — самодостаточный конспект на ~600-1000 строк с теорией, SQL, callouts и mini-quiz.

> [!tip] 🎯 Практические квизы — 420 вопросов
> К каждой лекции — 30 multiple-choice вопросов с ответами и объяснениями.
> Главный проект (project_id = 7): https://sdu.javazhan.tech/questions/7

### Quick links — все квизы

| # | Тема | Quiz URL |
|---|---|---|
| 01 | Introduction to Databases | https://sdu.javazhan.tech/questions/7/categories/22 |
| 02 | Relational Model | https://sdu.javazhan.tech/questions/7/categories/23 |
| 03 | SQL Basics | https://sdu.javazhan.tech/questions/7/categories/24 |
| 04 | Intermediate SQL | https://sdu.javazhan.tech/questions/7/categories/25 |
| 05 | Advanced SQL | https://sdu.javazhan.tech/questions/7/categories/26 |
| 06 | ER Model | https://sdu.javazhan.tech/questions/7/categories/27 |
| 07 | Normalization | https://sdu.javazhan.tech/questions/7/categories/28 |
| 08 | Complex Data Types | https://sdu.javazhan.tech/questions/7/categories/29 |
| 09 | Application Development | https://sdu.javazhan.tech/questions/7/categories/30 |
| 10 | Physical Storage | https://sdu.javazhan.tech/questions/7/categories/31 |
| 11 | Data Storage Structures | https://sdu.javazhan.tech/questions/7/categories/32 |
| 12 | Indexing | https://sdu.javazhan.tech/questions/7/categories/33 |
| 13 | Query Processing & Optimization | https://sdu.javazhan.tech/questions/7/categories/34 |
| 14 | Transactions | https://sdu.javazhan.tech/questions/7/categories/35 |

---

## How to read

1. Иди по порядку 01 → 14, если готовишься с нуля.
2. Прыгай по теме, если повторяешь нужный блок.
3. В конце каждой главы — **mini-quiz**: ответил ≥ 4 из 5 → можешь идти дальше.

> [!tip] Стратегия за 7 дней до финала
> День 1-2: 01 → 05 (модель + SQL).
> День 3: 06 + 07 (ER + normalization — обязательно тренировка декомпозиции).
> День 4: 08 + 09 (complex types + application).
> День 5: 10 + 11 + 12 (storage + indexing).
> День 6: 13 + 14 (query processing + transactions).
> День 7: повторение mini-quiz, проблемные места.

---

## Part 1. Foundations — основы

| # | Файл | Тема | Главное |
|---|---|---|---|
| 01 | [01-introduction-to-databases.md](01-introduction-to-databases.md) | Introduction to DBMS | DDL/DML/DCL/TCL, schema vs instance, 3-tier |
| 02 | [02-relational-model.md](02-relational-model.md) | Relational Model | tuple, attribute, keys, relational algebra |

**DBMS (Database Management System)** #abbreviation — система управления базой данных.

**relation** #dbterm — таблица в реляционной модели.

**primary key** #dbterm — уникальный идентификатор каждой строки.

> [!important] Без чего нельзя дальше
> Реляционная алгебра (σ, π, ⋈, ∪, −, ×) — это язык, в котором мыслит DBMS. Хорошо понимать SQL = переводить SQL → алгебру в голове.

---

## Part 2. SQL — язык запросов

| # | Файл | Тема | Главное |
|---|---|---|---|
| 03 | [03-sql-basics.md](03-sql-basics.md) | SQL Basics | SELECT, INSERT, UPDATE, DELETE, GROUP BY, базовые JOIN |
| 04 | [04-intermediate-sql.md](04-intermediate-sql.md) | Intermediate SQL | все JOIN-ы, подзапросы, CTE, views, constraints |
| 05 | [05-advanced-sql.md](05-advanced-sql.md) | Advanced SQL | functions, procedures, triggers, recursive CTE, window functions |

`SELECT col FROM table WHERE cond GROUP BY col HAVING cond ORDER BY col;` #sqlcommand
Базовый шаблон запроса. Порядок выполнения: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.

> [!warning] LEFT JOIN + WHERE на правую таблицу
> Превращает LEFT JOIN в INNER JOIN. Условие должно идти в `ON`. Главный exam trap по JOIN-ам.

> [!danger] SQL injection
> Никогда не склеивай user input в SQL-строку. Только prepared statements с параметрами `?` или `:param`.

---

## Part 3. Database Design — проектирование

| # | Файл | Тема | Главное |
|---|---|---|---|
| 06 | [06-er-model.md](06-er-model.md) | ER Model | entity, attribute, relationship, кардинальности, ISA, ER → таблицы |
| 07 | [07-normalization.md](07-normalization.md) | Normalization | FD, 1NF/2NF/3NF/BCNF, decomposition, lossless join |

**ERD (Entity-Relationship Diagram)** #abbreviation — диаграмма проектирования.

**functional dependency** #dbterm — `A → B`: зная A, всегда знаешь B.

**1NF / 2NF / 3NF / BCNF** #normalization — последовательные шаги нормализации.

> [!important] Алгоритм нормализации
> 1NF — все атомарно → 2NF — нет частичных зависимостей от PK → 3NF — нет транзитивных зависимостей → BCNF — каждая FD идёт от super key.

> [!tip] Memory hook
> `2NF` имеет смысл ТОЛЬКО при составном PK. Если PK один атрибут → 2NF выполняется автоматически.

---

## Part 4. Application Layer — приложения

| # | Файл | Тема | Главное |
|---|---|---|---|
| 08 | [08-complex-data-types.md](08-complex-data-types.md) | Complex Data Types | JSON/JSONB, arrays, composite types, temporal, spatial |
| 09 | [09-application-development.md](09-application-development.md) | Application Development | JDBC/ODBC, prepared statements, ORM, connection pool, sessions |

> [!warning] N+1 проблема
> ORM может молча выполнять 100 запросов вместо одного JOIN. Использовать `select_related` / eager loading.

---

## Part 5. Storage & Indexing — внутренности

| # | Файл | Тема | Главное |
|---|---|---|---|
| 10 | [10-physical-storage.md](10-physical-storage.md) | Physical Storage | hierarchy, HDD/SSD, RAID 0/1/5/10 |
| 11 | [11-data-storage-structures.md](11-data-storage-structures.md) | Storage Structures | slotted page, RID, buffer manager, MVCC |
| 12 | [12-indexing.md](12-indexing.md) | Indexing | B+ tree, hash, clustered, composite, covering |

**B+ tree** #dbterm — сбалансированное дерево, листья связаны в список — основа большинства индексов.

**RAID** #abbreviation — Redundant Array of Independent Disks: striping/mirroring/parity.

> [!important] Индекс — это всегда trade-off
> Ускоряет SELECT. Замедляет INSERT/UPDATE/DELETE. Занимает место. Создавай по реальным запросам, не "на всякий случай".

---

## Part 6. Query Processing — выполнение запросов

| # | Файл | Тема | Главное |
|---|---|---|---|
| 13 | [13-query-processing.md](13-query-processing.md) | Query Processing & Optimization | logical/physical plan, join algorithms, cost estimation |

**query optimizer** #dbterm — выбирает самый дешёвый план.

| Join algorithm | Когда |
|---|---|
| Nested-loop | маленькая R + индекс на S |
| Sort-merge | данные уже отсортированы |
| Hash | большие equi-join, есть RAM |

> [!tip] EXPLAIN ANALYZE
> Запускает запрос и показывает реальное время. Главный инструмент при оптимизации.

---

## Part 7. Transactions — транзакции

| # | Файл | Тема | Главное |
|---|---|---|---|
| 14 | [14-transactions.md](14-transactions.md) | Transactions | ACID, isolation levels, locking, deadlock, recovery, WAL |

**ACID** #abbreviation — Atomicity, Consistency, Isolation, Durability.

**deadlock** #dbterm — две транзакции блокируют друг друга.

**WAL (Write-Ahead Log)** #abbreviation — сначала лог, потом данные. Основа durability.

| Isolation level | Dirty | Non-repeatable | Phantom |
|---|---|---|---|
| Read uncommitted | возможно | возможно | возможно |
| Read committed | НЕТ | возможно | возможно |
| Repeatable read | НЕТ | НЕТ | возможно* |
| Serializable | НЕТ | НЕТ | НЕТ |

> [!danger] Exam trap — TRUNCATE vs DELETE
> `DELETE` — DML, в транзакции, можно `ROLLBACK`.
> `TRUNCATE` — DDL, авто-commit, обычно не откатить.

---

## Tag cheatsheet

| Тег | Когда использовать |
|---|---|
| `#abbreviation` | ACID, DDL, DML, DCL, TCL, ERD, DBMS, SQL, RAID, MVCC, WAL, CAP |
| `#sqlcommand` | SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, GRANT, BEGIN |
| `#dbterm` | primary key, foreign key, index, view, trigger, deadlock, MVCC |
| `#normalization` | 1NF, 2NF, 3NF, BCNF, 4NF |

---

## Cross-cutting связи между главами

- **02 → 03** — реляционная алгебра напрямую переводится в SQL.
- **02 → 07** — ключи и FD это математика normalization.
- **06 → 07** — ER переведён в таблицы → нормализуем.
- **04 → 09** — views и constraints используются приложением.
- **05 → 14** — transactions всплывают в triggers и procedures.
- **10 → 11 → 12** — диск → страница → индекс — снизу вверх.
- **12 → 13** — какие индексы есть → какой план выберет оптимизатор.
- **11 → 14** — buffer manager и checkpoint — часть recovery.

---

## Топ-10 exam questions (вероятностные)

1. Найди (X)+ по списку FD; определи candidate keys; нормализуй до 3NF.
2. Дано ER → нарисуй таблицы с PK/FK.
3. Объясни ACID и приведи пример нарушения каждого свойства.
4. На каком isolation level возможен phantom read? Почему?
5. Сравни B+ tree и hash index, когда какой использовать.
6. Объясни LEFT JOIN с условием в WHERE — почему может превратиться в INNER.
7. Чем `TRUNCATE` отличается от `DELETE` и `DROP`?
8. Что произойдёт в recursive CTE без условия выхода?
9. Объясни `EXPLAIN ANALYZE` plan и его операторы.
10. Защита от SQL injection — как и почему prepared statements.

> [!success] Если ты понимаешь все 14 глав
> Ты сдашь финал на достойный балл и сможешь пройти технический интервью на джуниор уровне по БД. Это не просто конспект для экзамена — это база для индустрии.
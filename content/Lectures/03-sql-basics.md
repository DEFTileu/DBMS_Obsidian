# 03 — SQL Basics

> Зачем эта тема: **SQL — главный язык работы с реляционной БД**. Без уверенного владения базовым SQL невозможно ни сдать финал, ни работать с любой БД на практике.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/24

---

## 1. Что такое SQL

**SQL (Structured Query Language)** — декларативный язык запросов к реляционным БД. Стандартизирован ISO/ANSI. #abbreviation

"Декларативный" = ты описываешь **что** нужно получить, а не **как** получать. DBMS сам решает, как именно искать данные.

> [!abstract] Главная идея
> Один SQL-запрос работает в Postgres, MySQL, Oracle, SQL Server (с небольшими отличиями). Это твой универсальный инструмент.

---

## 2. Подъязыки SQL

| Тип | Команды | Зачем |
|---|---|---|
| **DDL** | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` | структура БД |
| **DML** | `SELECT`, `INSERT`, `UPDATE`, `DELETE` | работа с данными |
| **DCL** | `GRANT`, `REVOKE` | права |
| **TCL** | `COMMIT`, `ROLLBACK`, `SAVEPOINT` | транзакции |

**DDL (Data Definition Language)** #abbreviation — создаёт/меняет структуру БД.

**DML (Data Manipulation Language)** #abbreviation — работает с данными.

---

## 3. Типы данных

| Категория | Примеры |
|---|---|
| **Числовые** | `INT`, `BIGINT`, `SMALLINT`, `DECIMAL(p,s)`, `NUMERIC`, `REAL`, `DOUBLE PRECISION` |
| **Строки** | `CHAR(n)`, `VARCHAR(n)`, `TEXT` |
| **Дата/время** | `DATE`, `TIME`, `TIMESTAMP`, `INTERVAL` |
| **Логика** | `BOOLEAN` |
| **Двоичные** | `BYTEA`, `BLOB` |
| **JSON** | `JSON`, `JSONB` (Postgres) |

> [!tip] CHAR vs VARCHAR
> - `CHAR(10)` — фиксированная длина, добивается пробелами.
> - `VARCHAR(10)` — переменная длина, до 10 символов.
> Используй `VARCHAR` почти всегда.

> [!warning] FLOAT для денег = боль
> Деньги храни в `DECIMAL(15,2)`, никогда не во `FLOAT`/`REAL`. Иначе округление съест копейки.

---

## 4. DDL — создание структуры

### 4.1 CREATE TABLE

```sql
CREATE TABLE customers (
    customer_id   INT          PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(255) UNIQUE,
    birth_date    DATE,
    balance       DECIMAL(15,2) DEFAULT 0 CHECK (balance >= 0),
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);
```

Расшифровка:
- `customer_id INT PRIMARY KEY` — первичный ключ.
- `NOT NULL` — обязательное поле.
- `UNIQUE` — уникальное значение.
- `CHECK (…)` — проверка значения.
- `DEFAULT …` — значение по умолчанию.

`CREATE TABLE name (col TYPE constraints, …);` #sqlcommand
Создаёт новую таблицу с указанными столбцами.

### 4.2 ALTER TABLE

```sql
ALTER TABLE customers ADD COLUMN phone VARCHAR(20);
ALTER TABLE customers DROP COLUMN phone;
ALTER TABLE customers ALTER COLUMN name TYPE VARCHAR(150);
ALTER TABLE customers RENAME COLUMN name TO full_name;
ALTER TABLE customers ADD CONSTRAINT chk_email CHECK (email LIKE '%@%');
```

`ALTER TABLE name ADD/DROP/ALTER COLUMN …;` #sqlcommand
Изменяет структуру существующей таблицы.

### 4.3 DROP и TRUNCATE

```sql
DROP TABLE customers;          -- удалить таблицу полностью
TRUNCATE TABLE customers;      -- очистить все строки (быстро)
```

> [!danger] Exam trap — DROP / TRUNCATE / DELETE
> | | DDL/DML | Что удаляет | Можно `WHERE`? | Откатить? |
> |---|---|---|---|---|
> | `DROP TABLE` | DDL | таблицу + данные | нет | нет |
> | `TRUNCATE TABLE` | DDL | все строки | нет | нет (обычно) |
> | `DELETE FROM` | DML | строки | да | да |

---

## 5. INSERT

```sql
-- Все столбцы по порядку
INSERT INTO customers VALUES (1, 'Aigerim', 'a@x.com', '2000-05-12', 0, NOW());

-- Только нужные столбцы
INSERT INTO customers (customer_id, name, email)
VALUES (2, 'Daulet', 'd@x.com');

-- Несколько строк сразу
INSERT INTO customers (customer_id, name) VALUES
    (3, 'Asel'),
    (4, 'Berik'),
    (5, 'Madi');

-- Из другой таблицы
INSERT INTO archive_customers (customer_id, name)
SELECT customer_id, name FROM customers WHERE created_at < '2020-01-01';
```

`INSERT INTO table (cols) VALUES (vals);` #sqlcommand
Добавляет одну или несколько строк в таблицу.

`INSERT INTO table (cols) SELECT …;` #sqlcommand
Копирует данные из другой таблицы.

> [!tip] Безопасный INSERT
> Всегда указывай столбцы явно `INSERT INTO t (col1, col2) VALUES …`. Иначе при добавлении нового столбца в таблицу старые INSERT сломаются.

---

## 6. SELECT — фундамент

### 6.1 Структура запроса

```sql
SELECT [DISTINCT] column1, column2, ...
FROM   table_name
WHERE  filter_condition
GROUP  BY column
HAVING group_filter
ORDER  BY column [ASC|DESC]
LIMIT  n OFFSET m;
```

Порядок ВЫПОЛНЕНИЯ (важно!):
```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

> [!important] Логический порядок выполнения
> `WHERE` фильтрует **до** группировки, `HAVING` — **после**. Поэтому в `WHERE` нельзя использовать агрегаты, а в `HAVING` — можно.

### 6.2 Простые SELECT

```sql
SELECT * FROM customers;
SELECT name, email FROM customers;
SELECT DISTINCT city FROM customers;
SELECT name AS full_name, balance * 1.1 AS new_balance FROM customers;
```

`SELECT col1, col2 FROM table;` #sqlcommand
Возвращает указанные столбцы из таблицы.

`DISTINCT` #sqlcommand — убирает дубликаты строк.

`AS alias` #sqlcommand — переименовывает столбец/таблицу в результате.

### 6.3 WHERE и операторы

```sql
SELECT * FROM customers WHERE balance > 1000;
SELECT * FROM customers WHERE name = 'Aigerim';
SELECT * FROM customers WHERE balance BETWEEN 100 AND 1000;
SELECT * FROM customers WHERE city IN ('Almaty', 'Astana');
SELECT * FROM customers WHERE name LIKE 'A%';        -- начинается на A
SELECT * FROM customers WHERE name LIKE '_aulet';    -- 6 букв, 2-я = a
SELECT * FROM customers WHERE email IS NULL;
SELECT * FROM customers WHERE balance > 0 AND city = 'Almaty';
```

| Оператор | Смысл |
|---|---|
| `=`, `<>`, `<`, `>`, `<=`, `>=` | сравнения |
| `BETWEEN a AND b` | в диапазоне (включительно) |
| `IN (…)` | принадлежит списку |
| `LIKE 'pattern'` | по шаблону (`%` — любая строка, `_` — один символ) |
| `IS NULL` / `IS NOT NULL` | проверка NULL |
| `AND`, `OR`, `NOT` | логика |

> [!warning] LIKE и индексы
> `LIKE 'A%'` использует индекс. `LIKE '%A'` или `LIKE '%A%'` — нет (full scan).

---

## 7. ORDER BY и LIMIT

```sql
SELECT name, balance FROM customers
ORDER BY balance DESC, name ASC
LIMIT 10 OFFSET 20;
```

- `ORDER BY` сортирует. `ASC` (по возрастанию, default) или `DESC`.
- Можно по нескольким столбцам.
- Можно по позиции: `ORDER BY 2 DESC` (2-й столбец из SELECT).
- `LIMIT n` — взять первые n строк.
- `OFFSET m` — пропустить m строк (для пагинации).

> [!tip] Pagination
> Для страницы 3 при 10 записях/стр: `LIMIT 10 OFFSET 20`. Но при больших offset — медленно. Лучше keyset pagination: `WHERE id > last_seen_id LIMIT 10`.

---

## 8. Агрегатные функции

| Функция | Что считает |
|---|---|
| `COUNT(*)` | кол-во строк |
| `COUNT(col)` | кол-во не-NULL значений |
| `COUNT(DISTINCT col)` | кол-во уникальных значений |
| `SUM(col)` | сумма |
| `AVG(col)` | среднее |
| `MIN(col)` | минимум |
| `MAX(col)` | максимум |

```sql
SELECT COUNT(*) FROM customers;
SELECT AVG(balance), MIN(balance), MAX(balance) FROM customers;
```

> [!warning] COUNT(*) vs COUNT(col)
> `COUNT(*)` считает ВСЕ строки.
> `COUNT(col)` считает только строки, где `col IS NOT NULL`.
> Часто это даёт разные числа.

---

## 9. GROUP BY и HAVING

```sql
SELECT city, COUNT(*) AS num_customers, AVG(balance) AS avg_bal
FROM   customers
GROUP  BY city
HAVING COUNT(*) > 10
ORDER  BY num_customers DESC;
```

`GROUP BY col` #sqlcommand — объединяет строки с одинаковым значением `col` в группы.

`HAVING condition` #sqlcommand — фильтрует группы (как `WHERE`, но после агрегации).

> [!important] Правило SELECT при GROUP BY
> В `SELECT` можно класть **только**: (а) столбцы из `GROUP BY`, (б) агрегаты. Всё остальное — ошибка (или мусор в MySQL).

```sql
-- ОШИБКА: name не в GROUP BY и не агрегат
SELECT city, name FROM customers GROUP BY city;

-- ОК
SELECT city, MIN(name) FROM customers GROUP BY city;
```

> [!danger] Exam trap — WHERE vs HAVING
> - `WHERE` фильтрует строки **до** группировки. Не может содержать агрегаты.
> - `HAVING` фильтрует группы **после** группировки. Может содержать агрегаты.

---

## 10. JOIN — основы

JOIN объединяет строки из нескольких таблиц.

### 10.1 INNER JOIN

Только строки, где есть совпадение в обеих таблицах.

```sql
SELECT c.name, a.balance
FROM   customers c
JOIN   accounts  a ON a.customer_id = c.customer_id;
```

`JOIN B ON A.x = B.x` #sqlcommand — INNER JOIN, оставляет только совпадения.

### 10.2 LEFT JOIN

Все строки из левой таблицы + совпадения из правой. Где нет совпадения → `NULL`.

```sql
SELECT c.name, a.balance
FROM   customers c
LEFT JOIN accounts a ON a.customer_id = c.customer_id;
```

Использование: "клиенты И их счета, **включая клиентов без счёта**".

### 10.3 Cartesian product (без ON)

```sql
SELECT * FROM customers, accounts;  -- m * n строк
```

> [!danger] Exam trap — забытый ON
> `JOIN` без `ON` или с условием на `=` всех к всем → cartesian product. Может вернуть миллионы строк.

### 10.4 Self join

Таблица соединяется сама с собой.

```sql
SELECT e.name AS employee, m.name AS manager
FROM   employees e
JOIN   employees m ON e.manager_id = m.emp_id;
```

> [!tip] Алиасы обязательны при self join
> Иначе DBMS не отличит "левую" и "правую" копию таблицы.

---

## 11. Подзапросы — введение

```sql
-- Скалярный подзапрос
SELECT name, balance,
       (SELECT AVG(balance) FROM customers) AS avg_bal
FROM customers;

-- Подзапрос в WHERE
SELECT name FROM customers
WHERE balance > (SELECT AVG(balance) FROM customers);

-- IN / EXISTS
SELECT name FROM customers
WHERE customer_id IN (SELECT customer_id FROM accounts WHERE balance > 1000);
```

`subquery` #sqlcommand — запрос внутри другого запроса.

`IN (subquery)` #sqlcommand — проверка принадлежности списку.

`EXISTS (subquery)` #sqlcommand — проверка существования хотя бы одной строки.

> [!warning] NULL в IN/NOT IN
> `WHERE x NOT IN (1, 2, NULL)` всегда вернёт UNKNOWN → ничего. Используй `NOT EXISTS` или фильтруй NULL заранее.

---

## 12. UPDATE

```sql
UPDATE customers
SET    balance = balance + 1000,
       updated_at = CURRENT_TIMESTAMP
WHERE  customer_id = 5;
```

`UPDATE table SET col = val WHERE …;` #sqlcommand
Изменяет существующие строки.

> [!danger] UPDATE без WHERE
> `UPDATE customers SET balance = 0;` обновит ВСЕ строки. Всегда проверяй `WHERE` дважды. Делай `SELECT` с тем же условием, прежде чем `UPDATE`.

---

## 13. DELETE

```sql
DELETE FROM customers WHERE customer_id = 5;
DELETE FROM customers WHERE created_at < '2010-01-01';
```

`DELETE FROM table WHERE …;` #sqlcommand
Удаляет строки. Без `WHERE` удалит всё (но таблица останется).

> [!tip] Пара UPDATE/DELETE
> Перед UPDATE/DELETE сначала запусти SELECT с тем же WHERE — увидишь, что именно изменится.

---

## 14. Полный пример — мини-банк

```sql
-- DDL
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    city        VARCHAR(50)
);

CREATE TABLE accounts (
    account_id  INT PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    balance     DECIMAL(15,2) CHECK (balance >= 0)
);

-- DML
INSERT INTO customers VALUES (1,'Aigerim','Almaty'), (2,'Daulet','Astana');
INSERT INTO accounts  VALUES (10,1,5000), (11,1,3000), (12,2,2000);

-- Аналитика
SELECT c.city,
       COUNT(a.account_id)  AS num_accounts,
       SUM(a.balance)       AS total_balance
FROM   customers c
LEFT  JOIN accounts a ON a.customer_id = c.customer_id
GROUP  BY c.city
HAVING SUM(a.balance) > 1000
ORDER  BY total_balance DESC;
```

---

## 15. Часто на экзамене

> [!danger] Exam traps
> 1. **WHERE vs HAVING** — `WHERE` до агрегации, `HAVING` после.
> 2. **GROUP BY + SELECT правило** — каждый non-aggregate столбец в SELECT должен быть в GROUP BY.
> 3. **NULL в WHERE** — `= NULL` не работает, нужен `IS NULL`.
> 4. **LIKE паттерны** — `%` любая строка, `_` ровно один символ.
> 5. **DELETE без WHERE** — удаляет всё.
> 6. **JOIN без ON** — cartesian product.
> 7. **DISTINCT и агрегаты** — `COUNT(DISTINCT col)` ≠ `COUNT(col)`.
> 8. **DROP / TRUNCATE / DELETE** — обязательно знать отличия.

---

## 16. Mini-quiz

1. В каком порядке DBMS выполняет `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`?
2. Что вернёт `SELECT COUNT(*)` vs `SELECT COUNT(col)`, если `col` имеет 3 NULL?
3. Чем `LIKE 'A%'` отличается от `LIKE '%A%'` по производительности?
4. Можно ли использовать `WHERE COUNT(*) > 5`?
5. Что произойдёт при `DELETE FROM customers` без `WHERE`?

> [!success] Если понял эту главу
> Ты можешь писать большинство ежедневных SQL-запросов: создавать таблицы, вставлять/обновлять/удалять, фильтровать, группировать, соединять. Дальше будет глубокая работа с JOIN-ами и подзапросами в Intermediate SQL.
# 04 — Intermediate SQL

> Зачем эта тема: базовый SELECT/INSERT мы знаем. Теперь учимся **соединять много таблиц**, писать **подзапросы**, создавать **views** и **constraints**. Это уровень, на котором SQL становится мощным инструментом.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/25

---

## 1. JOIN — все варианты

JOIN объединяет строки из 2+ таблиц по условию. Разница между JOIN-ами — в том, что делать со "несовпадающими" строками.

### 1.1 Сводная таблица JOIN-ов

| Тип | Что возвращает |
|---|---|
| `INNER JOIN` | только совпадения в ОБЕИХ |
| `LEFT JOIN` | все из ЛЕВОЙ + совпадения, иначе NULL |
| `RIGHT JOIN` | все из ПРАВОЙ + совпадения, иначе NULL |
| `FULL OUTER JOIN` | все из ОБЕИХ, NULL где нет совпадений |
| `CROSS JOIN` | декартово произведение (m × n) |
| `NATURAL JOIN` | INNER JOIN по всем общим столбцам автоматически |
| `SELF JOIN` | таблица с самой собой |

### 1.2 Визуализация (таблицы)

`employees`:
| emp_id | name | dept_id |
|---|---|---|
| 1 | Aigerim | 10 |
| 2 | Daulet | 20 |
| 3 | Asel | NULL |

`departments`:
| dept_id | dept_name |
|---|---|
| 10 | Sales |
| 30 | HR |

**INNER JOIN** (только пересечение):
| name | dept_name |
|---|---|
| Aigerim | Sales |

**LEFT JOIN** (все из employees):
| name | dept_name |
|---|---|
| Aigerim | Sales |
| Daulet | NULL |
| Asel | NULL |

**RIGHT JOIN** (все из departments):
| name | dept_name |
|---|---|
| Aigerim | Sales |
| NULL | HR |

**FULL OUTER JOIN** (все из обеих):
| name | dept_name |
|---|---|
| Aigerim | Sales |
| Daulet | NULL |
| Asel | NULL |
| NULL | HR |

> [!important] Mental model
> - `INNER` = пересечение.
> - `LEFT` = всё из левой + что нашлось из правой.
> - `RIGHT` = всё из правой + что нашлось из левой.
> - `FULL` = всё из обеих, дыры заполнены NULL.

### 1.3 Синтаксис

```sql
-- INNER (можно опустить слово INNER)
SELECT e.name, d.dept_name
FROM   employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;

-- LEFT
SELECT e.name, d.dept_name
FROM   employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;

-- FULL OUTER
SELECT e.name, d.dept_name
FROM   employees e
FULL OUTER JOIN departments d ON e.dept_id = d.dept_id;

-- CROSS (Cartesian)
SELECT e.name, d.dept_name FROM employees e CROSS JOIN departments d;

-- NATURAL JOIN — соединяет по всем общим столбцам
SELECT * FROM employees NATURAL JOIN departments;
```

`INNER JOIN B ON cond` #sqlcommand — соединение, оставляет только совпадения.

`LEFT JOIN B ON cond` #sqlcommand — все строки из левой таблицы.

`FULL OUTER JOIN B ON cond` #sqlcommand — все строки из обеих.

`CROSS JOIN B` #sqlcommand — декартово произведение.

`NATURAL JOIN B` #sqlcommand — INNER по всем общим именам столбцов.

> [!warning] NATURAL JOIN опасен
> Соединяет по ВСЕМ совпадающим именам — если в обеих таблицах есть `created_at`, то JOIN пойдёт и по нему тоже. Лучше явный `JOIN ... ON ...`.

### 1.4 USING — упрощённый синтаксис

Если столбцы соединения называются одинаково:
```sql
SELECT name, dept_name
FROM employees JOIN departments USING (dept_id);
```

`JOIN B USING (col)` #sqlcommand — упрощённый JOIN по одноимённым столбцам, при этом столбец `col` появляется один раз.

---

## 2. JOIN — типичные ловушки

### 2.1 LEFT JOIN + WHERE превращается в INNER

```sql
SELECT c.name, a.balance
FROM   customers c
LEFT JOIN accounts a ON a.customer_id = c.customer_id
WHERE  a.balance > 0;     -- ⚠️ убивает клиентов без счёта
```

`a.balance > 0` отсекает строки, где `a.balance = NULL`, а это как раз "клиенты без счёта". Эффект LEFT JOIN потерян.

**Правильно:** перенести условие в `ON`:
```sql
LEFT JOIN accounts a ON a.customer_id = c.customer_id AND a.balance > 0
```

> [!danger] Главный exam trap по JOIN
> Если в `WHERE` есть условие на столбцы правой таблицы LEFT JOIN-а, JOIN превращается в INNER. Условия на правую таблицу должны быть в `ON`.

### 2.2 Дубликаты при JOIN на 1-many

Если у клиента 3 счёта, JOIN вернёт 3 строки на этого клиента. Это нормально, но забудешь — посчитаешь общую сумму неверно.

```sql
-- ОПАСНО: завышает сумму
SELECT SUM(c.balance + a.balance)
FROM customers c JOIN accounts a ON a.customer_id = c.customer_id;
```

---

## 3. Подзапросы (subqueries)

### 3.1 Скалярный подзапрос

Возвращает одно значение. Можно использовать как литерал.

```sql
SELECT name, balance,
       balance - (SELECT AVG(balance) FROM customers) AS diff_from_avg
FROM customers;
```

### 3.2 Подзапрос в WHERE — IN / NOT IN

```sql
-- Клиенты, у которых есть счёт
SELECT name FROM customers
WHERE customer_id IN (SELECT customer_id FROM accounts);

-- Клиенты без счетов
SELECT name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM accounts);
```

> [!danger] NOT IN + NULL
> Если подзапрос вернёт хоть один NULL, **весь NOT IN вернёт пусто** (трёхзначная логика). Используй `NOT EXISTS` для безопасности.

### 3.3 EXISTS / NOT EXISTS

`EXISTS` возвращает TRUE, если подзапрос вернул хоть одну строку.

```sql
-- Клиенты с хотя бы одним счётом
SELECT name FROM customers c
WHERE EXISTS (
    SELECT 1 FROM accounts a WHERE a.customer_id = c.customer_id
);

-- Клиенты без счетов
SELECT name FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM accounts a WHERE a.customer_id = c.customer_id
);
```

> [!tip] EXISTS почти всегда лучше NOT IN
> EXISTS работает корректно с NULL и часто быстрее на больших объёмах.

### 3.4 Сравнение с ALL / ANY / SOME

```sql
-- Зарплата выше всех в IT
SELECT name FROM employees
WHERE salary > ALL (SELECT salary FROM employees WHERE dept = 'IT');

-- Зарплата выше хотя бы одного в IT
SELECT name FROM employees
WHERE salary > ANY (SELECT salary FROM employees WHERE dept = 'IT');
```

`ALL (subquery)` #sqlcommand — больше/меньше каждого.

`ANY/SOME (subquery)` #sqlcommand — больше/меньше хотя бы одного.

### 3.5 Коррелированные подзапросы

Подзапрос ссылается на внешний запрос. Выполняется для каждой строки внешнего.

```sql
SELECT c.name,
       (SELECT COUNT(*) FROM accounts a WHERE a.customer_id = c.customer_id) AS num_acc
FROM customers c;
```

> [!warning] Корреляция = N+1
> Подзапрос выполняется один раз на каждую строку. На больших таблицах — медленно. Часто переписывается через JOIN + GROUP BY.

### 3.6 Подзапрос в FROM (derived table)

```sql
SELECT city, AVG(num_acc) AS avg_accounts
FROM (
    SELECT c.city, COUNT(a.account_id) AS num_acc
    FROM customers c LEFT JOIN accounts a USING (customer_id)
    GROUP BY c.customer_id, c.city
) sub
GROUP BY city;
```

Алиас обязателен.

---

## 4. WITH — CTE (Common Table Expressions)

Именованный временный результат запроса. Читаемее вложенных подзапросов.

```sql
WITH city_stats AS (
    SELECT city, COUNT(*) AS num
    FROM customers
    GROUP BY city
),
big_cities AS (
    SELECT city FROM city_stats WHERE num > 10
)
SELECT * FROM customers WHERE city IN (SELECT city FROM big_cities);
```

`WITH name AS (subquery), …` #sqlcommand — определяет CTE, доступную в основном запросе.

> [!tip] Когда CTE
> - Когда логика сложная и нужно разбить на шаги.
> - Когда один и тот же подзапрос нужен дважды.
> - Когда нужна **рекурсивная** структура (см. ch5).

---

## 5. Set operations — UNION / INTERSECT / EXCEPT

```sql
SELECT name FROM customers
UNION
SELECT name FROM employees;        -- объединение, без дубликатов

SELECT name FROM customers
UNION ALL
SELECT name FROM employees;        -- объединение, с дубликатами

SELECT name FROM customers
INTERSECT
SELECT name FROM employees;        -- общие

SELECT name FROM customers
EXCEPT
SELECT name FROM employees;        -- в первой, но не во второй
```

| Оператор | Что делает | Дубликаты |
|---|---|---|
| `UNION` | объединение | убирает |
| `UNION ALL` | объединение | оставляет |
| `INTERSECT` | пересечение | убирает |
| `EXCEPT` | разность (Postgres) / `MINUS` (Oracle) | убирает |

> [!important] Условия set operations
> 1. Одинаковое количество столбцов.
> 2. Совместимые типы данных по позициям.
> 3. Имена столбцов берутся из первого SELECT.

> [!tip] UNION vs UNION ALL
> `UNION` дороже — нужна сортировка/хеширование для удаления дубликатов. Если знаешь, что дубликатов нет — используй `UNION ALL`.

---

## 6. CASE — условная логика

```sql
SELECT name, balance,
       CASE
           WHEN balance >= 100000 THEN 'VIP'
           WHEN balance >= 10000  THEN 'Regular'
           ELSE 'Basic'
       END AS tier
FROM customers;
```

Короткая форма (CASE на равенство):
```sql
SELECT name,
       CASE country
           WHEN 'KZ' THEN 'Kazakhstan'
           WHEN 'KG' THEN 'Kyrgyzstan'
           ELSE 'Other'
       END
FROM customers;
```

`CASE WHEN cond THEN val … ELSE val END` #sqlcommand — условное выражение в SQL.

> [!tip] CASE в агрегатах = pivot
> ```sql
> SELECT
>   SUM(CASE WHEN status='OK'   THEN 1 ELSE 0 END) AS ok_cnt,
>   SUM(CASE WHEN status='FAIL' THEN 1 ELSE 0 END) AS fail_cnt
> FROM transactions;
> ```
> Превращает строки в столбцы.

---

## 7. NULL в SQL

### 7.1 Функции для NULL

```sql
-- Заменить NULL на значение
SELECT name, COALESCE(phone, 'no phone') FROM customers;

-- Если a = b, вернуть NULL
SELECT NULLIF(division, 0) FROM stats;
```

`COALESCE(a, b, c)` #sqlcommand — возвращает первое не-NULL значение.

`NULLIF(a, b)` #sqlcommand — возвращает NULL, если `a = b`, иначе `a`.

### 7.2 NULL в агрегатах

- `COUNT(*)` считает все строки.
- `COUNT(col)`, `SUM`, `AVG` пропускают NULL.
- Если ВСЕ значения NULL → `SUM = NULL`, `AVG = NULL`, `COUNT(col) = 0`.

> [!warning] Среднее с NULL
> `AVG(balance)` игнорирует NULL. Если хочешь считать NULL как 0: `AVG(COALESCE(balance, 0))`.

---

## 8. Views — виртуальные таблицы

**view** — сохранённый SELECT-запрос, к которому можно обращаться как к таблице. #dbterm

```sql
CREATE VIEW vip_customers AS
SELECT customer_id, name, balance
FROM   customers
WHERE  balance >= 100000;

SELECT * FROM vip_customers WHERE name LIKE 'A%';
DROP VIEW vip_customers;
```

`CREATE VIEW name AS SELECT …;` #sqlcommand — создаёт view.

`DROP VIEW name;` #sqlcommand — удаляет view.

### 8.1 Зачем views

- **Безопасность** — пользователь видит только нужные столбцы/строки.
- **Упрощение** — сложный JOIN прячется за простым именем.
- **Логическая независимость** — если поменялась схема, можно адаптировать view, оставив запросы клиентов прежними.

### 8.2 Updatable views

Через view можно делать `INSERT/UPDATE/DELETE`, если:
- view над одной таблицей,
- нет агрегатов, `DISTINCT`, `GROUP BY`,
- все обязательные столбцы базовой таблицы доступны.

Иначе — read-only.

### 8.3 Materialized view

```sql
CREATE MATERIALIZED VIEW account_summary AS
SELECT customer_id, SUM(balance) AS total
FROM accounts GROUP BY customer_id;

REFRESH MATERIALIZED VIEW account_summary;
```

Хранит результат **физически**. Быстрый чтение, но устаревает — нужно `REFRESH`. Используется для аналитики.

| | View | Materialized view |
|---|---|---|
| Хранение | нет | есть, на диске |
| Скорость SELECT | как у запроса | быстро |
| Свежесть | всегда актуальна | устаревает |
| Refresh | не нужен | вручную/по расписанию |

> [!warning] Materialized view ≠ кеш
> Не "обновляется автоматически" в большинстве СУБД. Нужно REFRESH явно.

---

## 9. Integrity constraints

Правила, которые DBMS гарантирует на уровне таблицы.

| Constraint | Смысл |
|---|---|
| `NOT NULL` | значение обязательно |
| `UNIQUE` | значения уникальны (NULL допускаются) |
| `PRIMARY KEY` | уникальный ID, NOT NULL |
| `FOREIGN KEY` | ссылка на PK другой таблицы |
| `CHECK (cond)` | условие на значение |
| `DEFAULT val` | значение по умолчанию |

```sql
CREATE TABLE accounts (
    account_id  INT PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    type        VARCHAR(20) CHECK (type IN ('checking','savings','loan')),
    balance     DECIMAL(15,2) DEFAULT 0 CHECK (balance >= 0),
    UNIQUE(customer_id, type)
);
```

### 9.1 Именование constraints

```sql
ALTER TABLE accounts
    ADD CONSTRAINT chk_balance_nonneg CHECK (balance >= 0);

ALTER TABLE accounts DROP CONSTRAINT chk_balance_nonneg;
```

> [!tip] Зачем имя
> Без имени СУБД даст автоимя типа `accounts_balance_check_2`. Через год не вспомнишь, что это. Всегда давай осмысленные имена.

### 9.2 Deferrable constraints

```sql
CREATE TABLE … (
    …,
    FOREIGN KEY (parent_id) REFERENCES parents(id) DEFERRABLE INITIALLY DEFERRED
);
```

`DEFERRABLE` — проверка откладывается до конца транзакции. Полезно при циклических зависимостях.

---

## 10. Авторизация — DCL

```sql
-- Дать право
GRANT SELECT, INSERT ON customers TO clerk_role;
GRANT ALL PRIVILEGES ON accounts TO admin_role;

-- Отозвать
REVOKE INSERT ON customers FROM clerk_role;

-- С правом передачи дальше
GRANT SELECT ON customers TO analyst WITH GRANT OPTION;
```

`GRANT priv ON table TO user;` #sqlcommand — выдать право.

`REVOKE priv ON table FROM user;` #sqlcommand — отозвать право.

| Privilege | Действие |
|---|---|
| `SELECT` | читать |
| `INSERT` | вставлять |
| `UPDATE [(cols)]` | менять |
| `DELETE` | удалять |
| `REFERENCES` | использовать как FK |
| `ALL PRIVILEGES` | всё сразу |

> [!important] Roles
> На практике дают права не пользователю, а **роли**, потом назначают роль пользователю. Так проще управлять командой.

---

## 11. Транзакции — кратко (полное в ch17)

```sql
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;
COMMIT;       -- или ROLLBACK;
```

`BEGIN` / `START TRANSACTION` #sqlcommand — начало транзакции.

`COMMIT` #sqlcommand — зафиксировать изменения.

`ROLLBACK` #sqlcommand — откатить всё, что было после BEGIN.

> [!success] Главное правило
> Все изменения, которые должны произойти **вместе или никак**, оборачивай в одну транзакцию.

---

## 12. Часто на экзамене

> [!danger] Exam traps
> 1. **LEFT JOIN + WHERE на правую таблицу = INNER JOIN.** Условие должно идти в `ON`.
> 2. **NOT IN + NULL = пусто.** Используй `NOT EXISTS`.
> 3. **UNION vs UNION ALL** — `UNION` убирает дубликаты, `ALL` нет.
> 4. **View vs Materialized View** — view виртуальна, MV хранится.
> 5. **CHECK не может ссылаться на другие таблицы** в большинстве СУБД (используй триггер).
> 6. **GRANT на столбец** возможен для UPDATE: `GRANT UPDATE(balance) ON accounts TO …`.
> 7. **Foreign key ON DELETE** — варианты CASCADE/SET NULL/RESTRICT — знать все.

---

## 13. Mini-quiz

1. Чем `LEFT JOIN` + `WHERE B.col IS NULL` хорош для поиска "сирот"?
2. Почему `NOT IN (SELECT … WITH NULL)` опасен?
3. Какая разница между `UNION` и `UNION ALL` по производительности?
4. Можно ли делать `INSERT` через view? При каких условиях?
5. Что произойдёт при `ON DELETE CASCADE`, если удалить родительскую строку?

> [!success] Если понял эту главу
> Ты владеешь всеми типами JOIN-ов, умеешь писать подзапросы (включая EXISTS и коррелированные), работаешь с CTE, set-операциями, views и constraints. Теперь можно идти в advanced SQL: триггеры, процедуры, оконные функции.
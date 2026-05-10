# 05 — Advanced SQL

> Зачем эта тема: учимся **программировать на стороне БД** — функции, процедуры, триггеры, **рекурсивные** запросы и **window functions**. Это то, что отделяет крепкого мидла от джуна и стабильно появляется на финале.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/26

---

## 1. Stored Procedures и Functions

В БД можно хранить и выполнять код. Это даёт:
- **Производительность** — данные не гоняются по сети туда-обратно.
- **Переиспользование** — одна реализация для всех клиентов.
- **Безопасность** — пользователю можно дать право только на процедуру, а не на таблицу.

**stored procedure** — именованный блок кода, хранящийся в БД, вызывается через `CALL`. Может изменять данные. #dbterm

**function** — то же, но возвращает значение и используется внутри SELECT. #dbterm

| | Procedure | Function |
|---|---|---|
| Вызов | `CALL proc(...)` | `SELECT func(...)` |
| Возвращает | необязательно (OUT-параметры) | обязательно |
| В SELECT | нельзя | можно |
| Транзакции | можно управлять (COMMIT внутри) | обычно нельзя |
| Изменяет данные | да | в большинстве СУБД с ограничениями |

### 1.1 Function — пример (PostgreSQL)

```sql
CREATE OR REPLACE FUNCTION get_total_balance(cust_id INT)
RETURNS DECIMAL(15,2) AS $$
DECLARE
    total DECIMAL(15,2);
BEGIN
    SELECT COALESCE(SUM(balance), 0) INTO total
    FROM accounts WHERE customer_id = cust_id;
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- использование
SELECT name, get_total_balance(customer_id) AS total
FROM customers;
```

`CREATE FUNCTION name(params) RETURNS type AS $$ … $$ LANGUAGE plpgsql;` #sqlcommand
Создаёт функцию.

`DECLARE var TYPE;` — объявление локальной переменной.
`SELECT … INTO var` — записать результат в переменную.
`RETURN val;` — вернуть значение.

### 1.2 Procedure — пример

```sql
CREATE OR REPLACE PROCEDURE transfer(
    from_id INT,
    to_id   INT,
    amount  DECIMAL
) AS $$
BEGIN
    IF amount <= 0 THEN
        RAISE EXCEPTION 'Amount must be positive';
    END IF;

    UPDATE accounts SET balance = balance - amount WHERE account_id = from_id;
    UPDATE accounts SET balance = balance + amount WHERE account_id = to_id;
END;
$$ LANGUAGE plpgsql;

CALL transfer(1, 2, 1000);
```

`CREATE PROCEDURE name(params) AS $$ … $$ LANGUAGE plpgsql;` #sqlcommand
Создаёт процедуру.

`CALL name(args);` #sqlcommand
Вызывает процедуру.

`RAISE EXCEPTION 'msg';` — вызывает ошибку и откатывает транзакцию.

### 1.3 Управляющие конструкции PL/pgSQL

```sql
-- IF
IF balance < 0 THEN
    RAISE EXCEPTION 'Negative balance';
ELSIF balance > 1000000 THEN
    INSERT INTO vip_log VALUES (...);
ELSE
    -- nothing
END IF;

-- LOOP
FOR i IN 1..10 LOOP
    INSERT INTO test VALUES (i);
END LOOP;

-- WHILE
WHILE counter > 0 LOOP
    counter := counter - 1;
END LOOP;
```

> [!tip] Зачем функции в БД
> Считай: бэкенд делает 100 запросов к БД (каждый по сети) → или одна функция в БД, делающая всё внутри. Сеть в 100 раз дороже памяти.

---

## 2. Triggers

**trigger** — код, автоматически выполняемый DBMS при INSERT/UPDATE/DELETE на таблице. #dbterm

### 2.1 Зачем

- Автоматическое поддержание целостности (что не выразить через CHECK).
- Аудит — записать, кто и когда изменил данные.
- Каскадные изменения, которые не ложатся в FK.
- Денормализация (поддержание счётчиков, агрегатов).

### 2.2 Структура trigger в PostgreSQL

В Postgres триггер = **функция** + **trigger declaration**.

```sql
-- Функция-триггер
CREATE OR REPLACE FUNCTION log_balance_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance <> OLD.balance THEN
        INSERT INTO audit_log(account_id, old_bal, new_bal, changed_at)
        VALUES (OLD.account_id, OLD.balance, NEW.balance, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Сам триггер
CREATE TRIGGER trg_balance_audit
AFTER UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION log_balance_change();
```

`CREATE TRIGGER name BEFORE/AFTER event ON table FOR EACH ROW EXECUTE FUNCTION fn();` #sqlcommand
Создаёт триггер.

| Опция | Варианты |
|---|---|
| Время | `BEFORE`, `AFTER`, `INSTEAD OF` (для views) |
| Событие | `INSERT`, `UPDATE`, `DELETE`, `UPDATE OF col` |
| Уровень | `FOR EACH ROW`, `FOR EACH STATEMENT` |

### 2.3 Псевдо-таблицы NEW и OLD

| | OLD | NEW |
|---|---|---|
| `INSERT` | — | вставляемая строка |
| `UPDATE` | старая | новая |
| `DELETE` | удаляемая | — |

```sql
-- BEFORE INSERT — установить created_at
BEGIN
    NEW.created_at := NOW();
    RETURN NEW;
END;

-- AFTER DELETE — записать в архив
BEGIN
    INSERT INTO archived VALUES (OLD.*);
    RETURN OLD;
END;
```

### 2.4 BEFORE vs AFTER

- **BEFORE** — можно изменить `NEW`, можно отменить операцию (вернув NULL).
- **AFTER** — данные уже записаны, обычно для аудита/каскадов.

> [!warning] Триггеры — мина замедленного действия
> Триггер невидим для разработчика, читающего INSERT. Пишет лог, обновляет счётчик, дёргает другую таблицу — а ты не знаешь почему. Документируй и не злоупотребляй.

### 2.5 Включение / выключение

```sql
ALTER TABLE accounts DISABLE TRIGGER trg_balance_audit;
ALTER TABLE accounts ENABLE TRIGGER trg_balance_audit;
DROP TRIGGER trg_balance_audit ON accounts;
```

---

## 3. Рекурсивные запросы — WITH RECURSIVE

Используются для **иерархий** (сотрудник→менеджер, категория→подкатегория) и **графов**.

```sql
WITH RECURSIVE org_chart AS (
    -- Anchor: корни иерархии
    SELECT emp_id, name, manager_id, 1 AS level
    FROM   employees
    WHERE  manager_id IS NULL

    UNION ALL

    -- Recursive: добавить подчинённых на следующий уровень
    SELECT e.emp_id, e.name, e.manager_id, oc.level + 1
    FROM   employees e
    JOIN   org_chart oc ON e.manager_id = oc.emp_id
)
SELECT * FROM org_chart ORDER BY level, name;
```

`WITH RECURSIVE name AS (anchor UNION ALL recursive_part) …` #sqlcommand
Рекурсивная CTE: anchor + повторяющаяся часть, которая ссылается на саму CTE.

> [!important] Структура recursive CTE
> 1. **Anchor** — стартовый запрос (без рекурсии).
> 2. **UNION ALL**.
> 3. **Recursive part** — запрос, ссылающийся на саму CTE.
> 4. Условие выхода — когда `JOIN` перестаёт находить новые строки.

> [!warning] Бесконечная рекурсия
> Если в графе есть циклы — recursive CTE зациклится. Решение: добавить флаг "уже посетили" (массив пути).

---

## 4. Window functions

**window function** — агрегат, вычисляемый на "окне" вокруг строки, БЕЗ свёртки строк в одну. #dbterm

GROUP BY свернёт 100 строк в 1. Window function вернёт 100 строк с агрегатом для каждой.

### 4.1 Синтаксис

```sql
function() OVER (
    PARTITION BY col   -- разбить на группы (опционально)
    ORDER BY col       -- порядок внутри группы (для running/ranking)
    ROWS/RANGE …       -- границы окна (опционально)
)
```

`OVER (PARTITION BY … ORDER BY …)` #sqlcommand — задаёт окно.

### 4.2 Ranking functions

| Функция | Что делает |
|---|---|
| `ROW_NUMBER()` | уникальный номер строки в окне |
| `RANK()` | ранг с пропусками при равенстве (1, 2, 2, 4) |
| `DENSE_RANK()` | ранг без пропусков (1, 2, 2, 3) |
| `NTILE(n)` | разбить на n равных групп |

```sql
SELECT name, salary,
       RANK()       OVER (ORDER BY salary DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS rn
FROM employees;
```

### 4.3 Aggregates как window

```sql
-- Текущая сумма по дням (running total)
SELECT day, amount,
       SUM(amount) OVER (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM sales;

-- Среднее по последним 7 дням
SELECT day, amount,
       AVG(amount) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS avg_7d
FROM sales;
```

### 4.4 LAG / LEAD

```sql
-- Сравнить с предыдущим днём
SELECT day, amount,
       LAG(amount, 1) OVER (ORDER BY day) AS prev_day,
       amount - LAG(amount, 1) OVER (ORDER BY day) AS diff
FROM sales;
```

`LAG(col, n)` #sqlcommand — значение на n строк назад.

`LEAD(col, n)` #sqlcommand — значение на n строк вперёд.

### 4.5 PARTITION BY

```sql
-- Топ-3 зарплат В КАЖДОМ отделе
SELECT * FROM (
    SELECT name, dept_id, salary,
           DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rk
    FROM employees
) sub
WHERE rk <= 3;
```

> [!tip] PARTITION BY = "GROUP BY без свёртки"
> `PARTITION BY dept_id` = вычислять окно отдельно для каждого отдела, но строки сохранить.

> [!important] Window vs GROUP BY
> | Window | GROUP BY |
> |---|---|
> | Сохраняет все строки | Сворачивает в одну на группу |
> | Применяется ПОСЛЕ WHERE/GROUP BY | Применяется к строкам после WHERE |
> | Можно несколько разных окон | Одна группировка на запрос |

---

## 5. OLAP-расширения GROUP BY

Для аналитики поверх обычного GROUP BY.

### 5.1 ROLLUP — иерархические итоги

```sql
SELECT year, quarter, SUM(sales)
FROM sales
GROUP BY ROLLUP(year, quarter);
```
Даст: `(year, quarter)`, `(year)`, `()` — итоги по году + grand total.

### 5.2 CUBE — все комбинации

```sql
SELECT year, region, SUM(sales)
FROM sales
GROUP BY CUBE(year, region);
```
Даст: `(year, region)`, `(year)`, `(region)`, `()`.

### 5.3 GROUPING SETS — точный контроль

```sql
SELECT year, region, SUM(sales)
FROM sales
GROUP BY GROUPING SETS ((year, region), (year), ());
```

> [!tip] OLAP cheatsheet
> `ROLLUP(a, b)` = `(a, b), (a), ()`.
> `CUBE(a, b)` = `(a, b), (a), (b), ()`.
> `GROUPING SETS` = что хочешь, то и пишешь.

---

## 6. PIVOT — превратить строки в столбцы

В чистом SQL делается через `CASE` + `SUM`:

```sql
SELECT
    year,
    SUM(CASE WHEN region = 'KZ' THEN sales ELSE 0 END) AS kz,
    SUM(CASE WHEN region = 'KG' THEN sales ELSE 0 END) AS kg,
    SUM(CASE WHEN region = 'UZ' THEN sales ELSE 0 END) AS uz
FROM sales
GROUP BY year;
```

В Oracle/SQL Server есть отдельный `PIVOT` оператор. В Postgres — через `crosstab` extension.

---

## 7. Cursor — построчная обработка

**cursor** — указатель на строку результата запроса, позволяет обрабатывать строки по одной. #dbterm

```sql
DO $$
DECLARE
    cur CURSOR FOR SELECT account_id, balance FROM accounts;
    rec RECORD;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;
        IF rec.balance < 0 THEN
            UPDATE accounts SET frozen = TRUE WHERE account_id = rec.account_id;
        END IF;
    END LOOP;
    CLOSE cur;
END $$;
```

> [!warning] Cursor = медленно
> Построчная обработка отказывается от set-based мощи SQL. Используй только когда нельзя выразить через UPDATE/JOIN/window function. На больших данных cursor в 100 раз медленнее set-операции.

---

## 8. Транзакции в advanced коде

```sql
CREATE PROCEDURE transfer(...) AS $$
BEGIN
    BEGIN
        UPDATE accounts SET balance = balance - amt WHERE id = src;
        UPDATE accounts SET balance = balance + amt WHERE id = dst;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'Failed: %', SQLERRM;
            ROLLBACK;
    END;
END;
$$ LANGUAGE plpgsql;
```

> [!important] SAVEPOINT
> Можно откатить часть транзакции до отметки:
> ```sql
> BEGIN;
> UPDATE …;
> SAVEPOINT s1;
> UPDATE …;          -- что-то пошло не так
> ROLLBACK TO s1;    -- откатили только это
> COMMIT;            -- остальное зафиксируем
> ```

---

## 9. Часто на экзамене

> [!danger] Exam traps
> 1. **Procedure vs Function** — где можно вызвать в SELECT, где нет.
> 2. **NEW vs OLD** в триггерах — зависит от события.
> 3. **BEFORE vs AFTER** триггер — BEFORE может изменить NEW.
> 4. **Recursive CTE** — нужны anchor + UNION ALL + recursive part.
> 5. **RANK vs DENSE_RANK vs ROW_NUMBER** — отличие при равных значениях.
> 6. **PARTITION BY ≠ GROUP BY** — window не сворачивает строки.
> 7. **Cursor — антипаттерн** на больших данных.

---

## 10. Mini-quiz

1. Можно ли вызвать `procedure` внутри `SELECT`?
2. Что вернёт `NEW.balance` в triggere `BEFORE INSERT`? А в `AFTER DELETE`?
3. `RANK()` для зарплат `100, 100, 90` — какие значения вернёт?
4. Что произойдёт в recursive CTE без условия выхода?
5. В чём разница между `ROLLUP(a, b)` и `CUBE(a, b)`?

> [!success] Если понял эту главу
> Ты можешь писать функции, процедуры, триггеры, рекурсивные запросы по иерархиям, window functions для аналитики, OLAP-агрегаты. Это сильно отличает от тех, кто умеет только SELECT.
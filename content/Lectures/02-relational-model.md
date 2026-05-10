# 02 — The Relational Model

> Зачем эта тема: понять, **на чём математически стоит SQL**. Все таблицы, ключи и JOIN-ы — это формализм над множествами и кортежами. Без этой главы SQL остаётся набором заклинаний.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/23

---

## 1. Идея реляционной модели

Все данные = **таблицы**. Точка. Никаких деревьев, графов, документов. Только плоские таблицы со связями через значения.

Предложил **E. F. Codd** (1970, IBM). Получил Тьюринговскую премию за это.

> [!abstract] Главный принцип
> **Данные** хранятся в таблицах. **Связи** между таблицами устанавливаются через общие значения, а не через указатели/ссылки.

---

## 2. Базовые термины

**relation** — таблица в реляционной модели. Математически — подмножество декартова произведения. #dbterm

**tuple** — одна строка таблицы. #dbterm

**attribute** — столбец таблицы. #dbterm

**domain** — множество допустимых значений атрибута (например, `integer`, `varchar(50)`). #dbterm

**relation schema** — описание структуры: имя таблицы + список атрибутов с типами. #dbterm

**relation instance** — текущее множество строк в таблице. #dbterm

**degree (arity)** — количество атрибутов (столбцов). #dbterm

**cardinality** — количество кортежей (строк). #dbterm

> [!tip] Терминология двух миров
> **Математика:** relation, tuple, attribute, domain.
> **SQL:** table, row, column, data type.
> Это одно и то же, просто разные слова в разных контекстах.

```
employees(id, name, salary, dept_id)
   ↑                ↑
   schema           attributes
   
{(1, 'Aigerim', 500000, 10),
 (2, 'Daulet',  450000, 10),
 (3, 'Asel',    600000, 20)}    ← instance, cardinality = 3, degree = 4
```

---

## 3. Свойства реляции

1. **Каждая ячейка — атомарна** (нельзя положить в одну ячейку список или объект — это нарушит 1NF).
2. **Имена атрибутов уникальны** в пределах одной таблицы.
3. **Порядок столбцов не важен** (с точки зрения модели — на практике в SQL он влияет на `SELECT *`).
4. **Порядок строк не важен** — реляция это **множество**, а не список.
5. **Нет дубликатов кортежей** (в чистой модели; SQL по умолчанию допускает дубликаты).

> [!warning] SQL ≠ чистая модель
> SQL допускает дубликаты строк (multiset, не set), допускает `NULL`, и порядок строк виден через `ORDER BY`. Это инженерные компромиссы.

---

## 4. Ключи

Ключ — это атрибут (или комбинация), однозначно идентифицирующий кортеж.

| Тип ключа | Что это |
|---|---|
| **Super key** | любая комбинация атрибутов, которая уникально определяет строку |
| **Candidate key** | минимальный super key (нельзя выкинуть ни один атрибут) |
| **Primary key** | один из candidate keys, выбранный как основной |
| **Alternate key** | candidate keys, которые НЕ выбраны primary |
| **Foreign key** | атрибут, ссылающийся на primary key другой (или той же) таблицы |
| **Composite key** | ключ из нескольких атрибутов |

**primary key** — уникальный идентификатор каждой строки в таблице. Не может быть `NULL`, не может повторяться. #dbterm

**foreign key** — столбец, ссылающийся на primary key другой таблицы. Обеспечивает **referential integrity**. #dbterm

**super key** — любая комбинация атрибутов, которая уникальна. Может быть избыточной. #dbterm

**candidate key** — минимальный super key. #dbterm

```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    name    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE employees (
    emp_id    INT PRIMARY KEY,
    name      VARCHAR(100),
    email     VARCHAR(255) UNIQUE,
    dept_id   INT REFERENCES departments(dept_id)
);
```

`PRIMARY KEY` #sqlcommand — объявляет primary key столбец/комбинацию.

`UNIQUE` #sqlcommand — гарантирует уникальность, но допускает `NULL`.

`REFERENCES table(col)` #sqlcommand — объявляет foreign key.

> [!important] Правило про PK
> **PRIMARY KEY** = `NOT NULL` + `UNIQUE`. Всегда. Это не два атрибута, а одно встроенное правило.

> [!danger] Exam trap — UNIQUE vs PRIMARY KEY
> - **UNIQUE** допускает один `NULL` (или больше — зависит от СУБД).
> - **PRIMARY KEY** не допускает `NULL` вообще.
> - В таблице может быть много `UNIQUE`, но только один `PRIMARY KEY`.

---

## 5. Целостность

Реляционная модель навязывает три уровня целостности:

1. **Domain integrity** — значение должно соответствовать типу/домену (нельзя положить строку в `INT`).
2. **Entity integrity** — primary key не может быть `NULL`.
3. **Referential integrity** — foreign key должен указывать на существующую строку (или быть `NULL`).

```sql
CREATE TABLE accounts (
    account_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    balance DECIMAL(15,2) CHECK (balance >= 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

`CHECK (condition)` #sqlcommand — domain constraint, проверка значения.

`FOREIGN KEY … ON DELETE CASCADE` #sqlcommand — при удалении родителя удалить и потомков.

| ON DELETE | Что произойдёт |
|---|---|
| `CASCADE` | удалить связанные строки |
| `SET NULL` | поставить FK в NULL |
| `SET DEFAULT` | поставить FK в default |
| `RESTRICT` | запретить удаление родителя |
| `NO ACTION` | то же что RESTRICT, но проверяется в конце транзакции |

> [!warning] CASCADE опасен
> Удалил `departments` → автоматически удалились все `employees`. Часто это не то, что хочется. Используй с осторожностью.

---

## 6. Реляционная алгебра

Это формальный язык запросов. SQL — его практическая реализация. Знать её обязательно: на экзамене точно спросят.

### 6.1 Базовые операции

| Оператор | Символ | Что делает |
|---|---|---|
| **Selection** | σ (сигма) | выбирает строки по условию |
| **Projection** | π (пи) | выбирает столбцы |
| **Union** | ∪ | объединение двух реляций |
| **Set difference** | − | разность |
| **Cartesian product** | × | декартово произведение |
| **Rename** | ρ (ро) | переименование |

> [!tip] Memory hook — SPUDCR
> **S**election · **P**rojection · **U**nion · **D**ifference · **C**artesian · **R**ename — этого хватит, чтобы выразить любой запрос.

### 6.2 Selection σ

`σ_condition(R)` — берёт только те строки R, где условие истинно.

```
σ_salary > 500000 (employees)
```
SQL-эквивалент:
```sql
SELECT * FROM employees WHERE salary > 500000;
```

### 6.3 Projection π

`π_attr1, attr2(R)` — берёт только эти столбцы. **Дубликаты убираются** (в чистой алгебре).

```
π_name, salary (employees)
```
SQL:
```sql
SELECT DISTINCT name, salary FROM employees;
```

> [!warning] SQL без DISTINCT
> Чистая projection убирает дубликаты, но `SELECT name, salary FROM employees` — нет. Чтобы получить точную семантику π, нужен `SELECT DISTINCT`.

### 6.4 Union ∪

`R ∪ S` — все строки из R или S. Требует **union compatibility** (одинаковый набор атрибутов и совместимые типы).

```sql
SELECT name FROM customers
UNION
SELECT name FROM employees;
```

### 6.5 Difference −

`R − S` — все строки, которые есть в R, но нет в S.

```sql
SELECT name FROM customers
EXCEPT
SELECT name FROM employees;
```

### 6.6 Cartesian product ×

`R × S` — все возможные пары строк. Если R = m строк, S = n строк → результат m*n строк.

```sql
SELECT * FROM customers, accounts;  -- без WHERE → cartesian
```

### 6.7 Rename ρ

`ρ_new_name(R)` — переименовать таблицу или столбец.

```sql
SELECT e.name AS employee_name FROM employees AS e;
```

---

## 7. Производные операции

Эти операции выражаются через базовые, но используются постоянно:

### 7.1 Intersection ∩

`R ∩ S = R − (R − S)`

```sql
SELECT name FROM customers
INTERSECT
SELECT name FROM employees;
```

### 7.2 Natural join ⋈

`R ⋈ S` — Cartesian product + selection по равенству **общих** атрибутов + удаление дубликатов столбцов.

```sql
SELECT * FROM employees NATURAL JOIN departments;
```

### 7.3 Theta join ⋈_θ

JOIN по произвольному условию.

```
employees ⋈_(emp.dept_id = dept.id) departments
```
```sql
SELECT * FROM employees e JOIN departments d ON e.dept_id = d.id;
```

### 7.4 Outer join

Сохраняет строки одной таблицы, даже если совпадений нет:
- **Left outer join** ⟕ — все строки из левой.
- **Right outer join** ⟖ — все строки из правой.
- **Full outer join** ⟗ — все строки из обеих.

Несовпадающие места заполняются `NULL`.

### 7.5 Division ÷

`R ÷ S` — все значения в R, которые встречаются со ВСЕМИ значениями из S. Используется для запросов типа "клиенты, у которых есть счета во всех филиалах".

> [!important] Division — частая хитрость
> SQL не имеет прямого оператора division. Реализуется через двойное `NOT EXISTS` или `GROUP BY HAVING COUNT = (полный счёт)`.

---

## 8. Алгебра → SQL: примеры

### Пример 1
"Имена сотрудников, чья зарплата > 500K"
```
π_name (σ_salary > 500000 (employees))
```
```sql
SELECT name FROM employees WHERE salary > 500000;
```

### Пример 2
"Имена сотрудников и название их отдела"
```
π_name, dept_name (employees ⋈_dept_id departments)
```
```sql
SELECT e.name, d.dept_name
FROM employees e JOIN departments d ON e.dept_id = d.dept_id;
```

### Пример 3
"Клиенты, у которых нет счёта"
```
π_id(customers) − π_customer_id(accounts)
```
```sql
SELECT id FROM customers
EXCEPT
SELECT customer_id FROM accounts;
```

> [!tip] Стратегия чтения SQL → алгебра
> 1. `WHERE` → σ
> 2. `SELECT col1, col2` → π
> 3. `FROM A JOIN B ON …` → ⋈
> 4. `UNION/EXCEPT/INTERSECT` → ∪/−/∩

---

## 9. NULL и три значения логики

`NULL` — отсутствие значения. Логика становится трёхзначной: `TRUE`, `FALSE`, `UNKNOWN`.

| Выражение | Результат |
|---|---|
| `NULL = NULL` | UNKNOWN (не TRUE!) |
| `NULL <> 5` | UNKNOWN |
| `5 + NULL` | NULL |
| `NULL OR TRUE` | TRUE |
| `NULL AND FALSE` | FALSE |
| `NULL OR FALSE` | UNKNOWN |

`WHERE` пропускает только строки, где условие = TRUE. Поэтому `WHERE col = NULL` ничего не вернёт. Правильно: `WHERE col IS NULL`.

> [!danger] Exam trap — NULL comparison
> `col = NULL` ВСЕГДА UNKNOWN, даже если `col` действительно `NULL`.
> Используй `IS NULL` / `IS NOT NULL`.

---

## 10. Связь реляционной модели и SQL

| Реляционная модель | SQL |
|---|---|
| relation | table |
| tuple | row |
| attribute | column |
| domain | data type |
| set semantics | bag/multiset (по умолчанию) |
| без NULL | с NULL |
| без ORDER BY | с ORDER BY |

> [!success] Если понял эту главу
> Ты понимаешь: каждая SQL-конструкция переводится в реляционную алгебру. JOIN-ы, GROUP BY, WHERE — это просто красивая обёртка над σ, π, ⋈.

---

## 11. Часто на экзамене

> [!danger] Exam traps
> 1. **PRIMARY KEY vs UNIQUE** — отличие по NULL и количеству на таблицу.
> 2. **NULL semantics** — `= NULL` всегда UNKNOWN.
> 3. **Cartesian product без условия** — экспоненциальный взрыв строк.
> 4. **Natural join** убирает дубликаты столбцов с одинаковым именем — следить, какие колонки реально совпадают.
> 5. **Union compatibility** — для `UNION` обе реляции должны иметь одинаковую арность и совместимые типы.
> 6. **Division** — выражается через двойное NOT EXISTS.

---

## 12. Mini-quiz

1. Какая разница между super key и candidate key?
2. Что вернёт `SELECT * FROM A, B` если в A 100 строк, в B 50?
3. Как выразить `INTERSECT` через базовые операции реляционной алгебры?
4. Почему `WHERE name = NULL` не работает?
5. В чём разница между natural join и theta join?

> [!success] Итог главы
> Реляционная модель = **таблицы + ключи + алгебра**. SQL — это диалект для людей, но математика под ним — это σ, π, ⋈, ∪, −, ×.
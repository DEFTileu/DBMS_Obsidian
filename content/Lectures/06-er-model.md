# 06 — Entity-Relationship (ER) Model

> Зачем эта тема: прежде чем создавать таблицы, нужно **спроектировать** БД. ER-модель — стандартный способ нарисовать схему до кода. Финал любит "по этому ER нарисуй таблицы" — за это легко взять баллы.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/27

---

## 1. Идея ER-модели

Реальный мир описывается через:
- **сущности** (то, что есть): клиент, счёт, кредит;
- **атрибуты** (свойства сущностей): имя, баланс;
- **связи** между сущностями: "клиент **имеет** счёт".

Эту картину рисуют в виде **ERD** (Entity-Relationship Diagram), потом переводят в таблицы.

> [!abstract] Главная идея
> ER — это **визуальный язык**, чтобы обсуждать схему БД ДО написания SQL. Сделал ERD → перевёл в таблицы → нормализовал → DDL.

**ERD (Entity-Relationship Diagram)** — диаграмма сущностей и связей. #abbreviation

**entity** — объект реального мира, который мы хотим хранить (клиент, заказ). #dbterm

**attribute** — свойство сущности или связи. #dbterm

**relationship** — связь между сущностями. #dbterm

---

## 2. Сущности (Entities)

### 2.1 Виды

- **Strong entity (regular)** — существует независимо, имеет собственный PK.
- **Weak entity** — не существует без "родителя", PK составной = (FK на родителя + дискриминатор).

```
Strong:  CUSTOMER(customer_id PK, name)
Weak:    DEPENDENT(dependent_no, name) — слабая, ключом только в паре с EMPLOYEE.
```

### 2.2 Обозначения на ERD

- **Прямоугольник** — entity (двойной для weak).
- **Овал** — attribute.
- **Ромб** — relationship.
- Линии соединяют ромб и сущности.

> [!tip] Пример обозначений
> ```
> [CUSTOMER] ── (has) ── [ACCOUNT]
>     │                       │
>    {name}                 {balance}
> ```

---

## 3. Атрибуты (Attributes)

| Тип атрибута | Описание | Пример |
|---|---|---|
| **Simple (atomic)** | неделимый | `email`, `age` |
| **Composite** | состоит из частей | `address(street, city, zip)` |
| **Single-valued** | одно значение | `birth_date` |
| **Multi-valued** | несколько значений | `phone_numbers` |
| **Derived** | вычисляется | `age` из `birth_date` |
| **Stored** | хранится | `birth_date` |
| **Key** | уникальный идентификатор | `passport_no` |

> [!warning] Multi-valued + composite
> Атрибут "адреса клиента" (несколько штук, у каждого — улица, город) — это composite multi-valued. В реляционной модели → отдельная таблица.

### 3.1 Обозначения

- Овал — обычный атрибут.
- Двойной овал — multi-valued.
- Пунктирный овал — derived.
- Подчёркивание — primary key.
- Овал с овалами внутри — composite.

---

## 4. Ключи

**super key** — атрибут или комбинация, уникальная для сущности. #dbterm

**candidate key** — минимальный super key. #dbterm

**primary key** — выбранный candidate key. #dbterm

**partial key (discriminator)** — атрибут, уникальный В ПРЕДЕЛАХ родителя для weak entity. #dbterm

```
EMPLOYEE(emp_id PK)
DEPENDENT(dependent_no — partial key)
   → PK(DEPENDENT) = (emp_id, dependent_no)
```

---

## 5. Связи (Relationships)

Связь = отношение между двумя или более сущностями.

### 5.1 Степень (degree) связи

| Степень | Кол-во сущностей |
|---|---|
| **Unary** (recursive) | 1 — `EMPLOYEE` "manages" `EMPLOYEE` |
| **Binary** | 2 — `CUSTOMER` "has" `ACCOUNT` |
| **Ternary** | 3 — `DOCTOR` "prescribes" `MEDICINE` "to" `PATIENT` |

### 5.2 Кардинальность (cardinality)

Сколько экземпляров одной сущности связано со сколькими другой.

| Тип | Запись | Пример |
|---|---|---|
| **One-to-One** | 1:1 | человек — паспорт |
| **One-to-Many** | 1:N | клиент — счета |
| **Many-to-One** | N:1 | счета — клиент |
| **Many-to-Many** | M:N | студент — курс |

> [!important] Самое важное соотношение
> 1:N — клиент имеет много счетов, счёт принадлежит одному клиенту. Это переводится так:
> - В таблице "many" (`accounts`) появляется `customer_id` как FK.

### 5.3 Participation (участие)

| Тип | Что значит |
|---|---|
| **Total (mandatory)** | каждая сущность ОБЯЗАНА участвовать (двойная линия) |
| **Partial (optional)** | может, а может и нет (одинарная линия) |

```
CUSTOMER ═══ has ─── ACCOUNT       ← каждый счёт обязан принадлежать клиенту,
                                     но клиент может быть без счёта
```

### 5.4 Обозначение (Chen vs Crow's Foot)

**Chen** (классический):
- `1` или `N` подписывается на линии.
- `(min, max)` — точная кардинальность.

**Crow's Foot** (современный, как в DBeaver/Lucid):
- Линия с "лапкой" — many.
- Кружок — optional, чёрточка — mandatory, "одна".

---

## 6. Атрибуты на связях

Связь сама может иметь атрибуты, особенно при M:N.

```
STUDENT ── (enrolled_in) ── COURSE
                │
              {grade, semester}
```

При переводе в таблицу:
```sql
CREATE TABLE enrollment (
    student_id INT REFERENCES students(id),
    course_id  INT REFERENCES courses(id),
    grade      CHAR(1),
    semester   VARCHAR(20),
    PRIMARY KEY (student_id, course_id, semester)
);
```

---

## 7. Weak entities

**weak entity** — сущность, которая не имеет собственного PK; идентифицируется только в связи с владельцем (identifying entity). #dbterm

Примеры:
- `DEPENDENT` без `EMPLOYEE` — не имеет смысла.
- `ORDER_LINE` без `ORDER` — не имеет смысла.
- `PAYMENT` без `LOAN` — обычно не имеет.

PK weak = PK сильной + partial key.

```
EMPLOYEE(emp_id PK)
DEPENDENT(dependent_no, name, …)
PK(DEPENDENT) = (emp_id, dependent_no)
```

> [!tip] Признак weak entity
> Можно ли удалить родителя без удаления потомка? Если нет — потомок weak.

---

## 8. Специализация и обобщение (ISA)

**ISA** ("is-a") — наследование между сущностями. #abbreviation

```
        PERSON
         /  \
   EMPLOYEE  STUDENT
```

`EMPLOYEE` ISA `PERSON` → каждый сотрудник также является человеком.

### 8.1 Disjoint vs Overlapping

- **Disjoint** — каждый экземпляр родителя относится МАКСИМУМ к одному потомку.
- **Overlapping** — может быть в нескольких (студент И сотрудник одновременно).

### 8.2 Total vs Partial

- **Total specialization** — каждый родитель ОБЯЗАН быть в одном из потомков.
- **Partial** — может быть просто `PERSON` без подкатегории.

### 8.3 Перевод ISA в таблицы — три варианта

1. **Один большой стол** — все атрибуты в `PERSON`, плюс `type` дискриминатор. Много NULL для специализированных столбцов.
2. **Таблица на каждого потомка** — `EMPLOYEE`, `STUDENT` с собственным PK + общие атрибуты дублированы. Нет NULL, но дублирование.
3. **Общая + специализированные** — `PERSON` + `EMPLOYEE(person_id FK)` + `STUDENT(person_id FK)`. Самый "чистый", но JOIN-ы.

> [!important] Какой вариант выбрать
> Зависит от запросов. Если часто читать всех людей разом — вариант 1 или 3. Если потомки разные и редко смешиваются — вариант 2.

---

## 9. Aggregation

Когда связь сама становится "сущностью" в другой связи.

```
EMPLOYEE — works_on — PROJECT     ← связь
              ↑
          MANAGER    monitors    ← связь над связью
```

В чистой ER ассоциация связи не может участвовать в другой связи. Aggregation позволяет это.

> [!tip] На практике
> Чаще всего проще ввести искусственную сущность вместо aggregation: `WorkOn(emp_id, project_id, ...)` как отдельная сущность с отношениями к менеджерам.

---

## 10. ER → Relations: алгоритм перевода

### Шаг 1. Strong entity → таблица
- Атрибуты → столбцы.
- Composite → разложить на простые столбцы.
- Multi-valued → отдельная таблица.
- PK сущности → PK таблицы.

```
CUSTOMER(customer_id PK, name, address(street, city, zip))
       ↓
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(100),
    street VARCHAR(100),
    city VARCHAR(50),
    zip VARCHAR(10)
);
```

### Шаг 2. Multi-valued → отдельная таблица
```
CUSTOMER {{phone_numbers}}
       ↓
CREATE TABLE customer_phones (
    customer_id INT REFERENCES customers,
    phone VARCHAR(20),
    PRIMARY KEY (customer_id, phone)
);
```

### Шаг 3. Weak entity → таблица с PK = (PK сильной + partial key)

```
EMPLOYEE(emp_id) — has — DEPENDENT(dependent_no, name)
       ↓
CREATE TABLE dependents (
    emp_id        INT REFERENCES employees,
    dependent_no  INT,
    name          VARCHAR(100),
    PRIMARY KEY (emp_id, dependent_no)
);
```

### Шаг 4. Перевод связей

| Связь | Как переводить |
|---|---|
| **1:1** | FK в любой из двух (предпочесть с total participation), либо объединить таблицы |
| **1:N** | FK в таблице "many" |
| **M:N** | отдельная связующая таблица с FK на оба + атрибуты связи |
| **Recursive 1:N** | self FK |
| **Recursive M:N** | связующая таблица с двумя FK на ту же таблицу |
| **Ternary** | связующая таблица с тремя FK |

### 10.1 1:N — пример

```
CUSTOMER ── (has) ── ACCOUNT       (1:N)
       ↓
CREATE TABLE customers (id PK, name);
CREATE TABLE accounts  (id PK, balance, customer_id REFERENCES customers);
```

### 10.2 M:N — пример

```
STUDENT ── (enrolls_in) ── COURSE       (M:N)
                │
              grade
       ↓
CREATE TABLE students  (id PK, name);
CREATE TABLE courses   (id PK, title);
CREATE TABLE enrollments (
    student_id INT REFERENCES students,
    course_id  INT REFERENCES courses,
    grade      CHAR(1),
    PRIMARY KEY (student_id, course_id)
);
```

### 10.3 Recursive 1:N — пример

```
EMPLOYEE — manages — EMPLOYEE       (1:N — менеджер управляет многими)
       ↓
CREATE TABLE employees (
    emp_id     INT PRIMARY KEY,
    name       VARCHAR(100),
    manager_id INT REFERENCES employees(emp_id)
);
```

> [!important] Алгоритм перевода — запомнить порядок
> 1. Сильные сущности → таблицы.
> 2. Multi-valued → отдельные таблицы.
> 3. Слабые сущности → таблицы с составным PK.
> 4. Связи 1:1 → FK.
> 5. Связи 1:N → FK в "many".
> 6. Связи M:N → связующая таблица.

---

## 11. Полный пример — банк (мини-ERD)

**Сущности:**
- `CUSTOMER(customer_id, name, address(...))` — strong
- `ACCOUNT(account_id, balance, type)` — strong
- `LOAN(loan_id, amount)` — strong
- `BRANCH(branch_id, name, city)` — strong
- `EMPLOYEE(emp_id, name)` — strong, recursive `manages`

**Связи:**
- `CUSTOMER` 1:N `ACCOUNT` — у клиента много счетов, счёт у одного клиента.
- `CUSTOMER` M:N `LOAN` — клиент может иметь много кредитов, у кредита может быть несколько созаёмщиков.
- `BRANCH` 1:N `ACCOUNT` — у филиала много счетов.
- `EMPLOYEE` recursive 1:N `manages`.

**Перевод:**
```sql
CREATE TABLE customers (customer_id PRIMARY KEY, name, street, city, zip);
CREATE TABLE branches  (branch_id PRIMARY KEY, name, city);
CREATE TABLE accounts  (
    account_id PRIMARY KEY, balance, type,
    customer_id REFERENCES customers,
    branch_id   REFERENCES branches
);
CREATE TABLE loans (loan_id PRIMARY KEY, amount, branch_id REFERENCES branches);
CREATE TABLE customer_loans (              -- M:N
    customer_id REFERENCES customers,
    loan_id     REFERENCES loans,
    PRIMARY KEY (customer_id, loan_id)
);
CREATE TABLE employees (
    emp_id PRIMARY KEY, name,
    manager_id REFERENCES employees(emp_id)
);
```

---

## 12. Enhanced ER (EER)

EER расширяет классическую ER:
- ISA / specialization / generalization.
- Aggregation.
- Categorization (объединение разных типов в подкласс).

> [!tip] Когда EER
> Когда модель сложнее банка — например, общественный портал с множеством типов пользователей, или e-commerce с разными типами товаров.

---

## 13. Часто на экзамене

> [!danger] Exam traps
> 1. **Weak vs strong** — у weak нет собственного PK, PK = parent_PK + partial_key.
> 2. **1:1 — FK куда** — на сторону с total participation, чтобы избежать NULL.
> 3. **M:N → связующая таблица** — обязательно с PK = (FK1, FK2).
> 4. **Multi-valued → отдельная таблица** — нельзя оставлять как столбец.
> 5. **Composite атрибут** — раскладывается на простые столбцы (ну или объединяется в JSON).
> 6. **Total vs partial participation** — двойная линия = total.
> 7. **Recursive M:N** — связующая таблица с двумя FK на ту же таблицу + разные роли.

---

## 14. Mini-quiz

1. У сущности `BOOK_COPY` нет собственного ID, только номер копии в пределах книги. Какая это сущность?
2. Как перевести связь "сотрудник работает на проект" с атрибутом `hours`?
3. Куда положить FK при 1:1 связи `PERSON` ↔ `PASSPORT`?
4. Что нарисует двойная линия от entity к relationship?
5. Зачем нужен ISA, если можно сделать одну таблицу с `type` колонкой?

> [!success] Если понял эту главу
> Ты можешь нарисовать ER по словесному ТЗ и перевести его в работающие таблицы. Это база, на которой строится всё проектирование БД.
# 07 — Database Normalization

> Зачем эта тема: **нормализация** — процесс приведения схемы БД к виду без избыточности и аномалий. На финале это almost guaranteed: дано "плохая таблица" → нормализуй. Нужно знать FD, 1NF, 2NF, 3NF, BCNF и уметь применять их пошагово.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/28

---

## 1. Зачем нормализовать

Плохая таблица создаёт **аномалии**:

| Аномалия | Что происходит |
|---|---|
| **Update anomaly** | одно изменение надо делать в N местах, иначе данные расходятся |
| **Insert anomaly** | нельзя вставить новую сущность без "прицепа" другой |
| **Delete anomaly** | удалив одну строку, теряешь информацию о другой сущности |
| **Redundancy** | одни и те же данные хранятся много раз |

### Пример плохой таблицы

| order_id | customer_id | customer_name | customer_city | product | qty |
|---|---|---|---|---|---|
| 1 | C1 | Aigerim | Almaty | Pen | 2 |
| 2 | C1 | Aigerim | Almaty | Notebook | 1 |
| 3 | C2 | Daulet | Astana | Pen | 5 |

Проблемы:
- Если Aigerim переехала → надо менять в двух строках (update anomaly).
- Нельзя записать клиента, у которого ещё нет заказа (insert anomaly).
- Если удалить заказ #3 → теряем факт существования Daulet (delete anomaly).
- "Aigerim, Almaty" повторяется (redundancy).

> [!abstract] Цель нормализации
> Разбить таблицу на части так, чтобы **каждый факт хранился ровно один раз**.

---

## 2. Functional Dependencies (FD)

**FD** A → B значит: **зная A, всегда знаешь B**. Один и тот же A → один и тот же B. #dbterm

```
customer_id → customer_name, customer_city
order_id    → customer_id, product, qty
```

Запись `A → B`: A называется determinant, B — dependent.

### 2.1 Свойства FD (axioms Armstrong)

1. **Reflexivity:** если B ⊆ A, то A → B.
2. **Augmentation:** если A → B, то AC → BC.
3. **Transitivity:** если A → B и B → C, то A → C.

Производные:
- **Union:** A → B и A → C ⇒ A → BC.
- **Decomposition:** A → BC ⇒ A → B и A → C.

### 2.2 Closure FD

`(X)+` — closure (замыкание) X = все атрибуты, которые можно вывести из X через FD.

Если `(X)+ = всё в таблице`, то X — super key.
Если ещё минимальный — candidate key.

> [!important] Алгоритм нахождения closure
> 1. Начать с `result = X`.
> 2. Для каждой FD `A → B`: если `A ⊆ result`, добавить B в result.
> 3. Повторять, пока result растёт.

---

## 3. Ключи в контексте FD

| Тип | Что это |
|---|---|
| **Super key** | X такой, что (X)+ = все атрибуты |
| **Candidate key** | минимальный super key |
| **Primary key** | выбранный candidate key |
| **Prime attribute** | атрибут, входящий в какой-нибудь candidate key |
| **Non-prime attribute** | не входит ни в один candidate key |

---

## 4. Нормальные формы — обзор

| NF | Условие |
|---|---|
| **1NF** | все значения атомарны, нет повторяющихся групп |
| **2NF** | 1NF + нет частичной зависимости non-prime от candidate key |
| **3NF** | 2NF + нет транзитивной зависимости non-prime |
| **BCNF** | для каждой нетривиальной FD A → B, A — super key |
| **4NF** | BCNF + нет нетривиальных multi-valued зависимостей |
| **5NF** | 4NF + нет join зависимостей (редко требуется) |

> [!tip] Memory hook
> **1** — атомарность.
> **2** — частичные зависимости.
> **3** — транзитивные зависимости.
> **BCNF** — каждый detrminant — super key.

---

## 5. 1NF — First Normal Form #normalization

**Правило:** все значения атомарны, нет повторяющихся групп и multi-valued атрибутов.

### Плохо (нарушает 1NF):

| student_id | name | courses |
|---|---|---|
| 1 | Aigerim | DB, OS, Algo |
| 2 | Daulet | DB |

`courses` — список → не атомарно.

### Хорошо:

| student_id | name | course |
|---|---|---|
| 1 | Aigerim | DB |
| 1 | Aigerim | OS |
| 1 | Aigerim | Algo |
| 2 | Daulet | DB |

Или ещё лучше — разбить на две:
```
students(student_id, name)
enrollments(student_id, course)
```

> [!warning] 1NF и JSON
> JSON-столбец формально нарушает 1NF. Современные СУБД (Postgres) умеют с ним работать, но для нормализации он "не атомарен".

---

## 6. 2NF — Second Normal Form #normalization

**Правило:** 1NF + у каждого non-prime атрибута нет ЧАСТИЧНОЙ зависимости от candidate key.

> Имеет смысл только если PK составной.

### Плохо

```
order_lines(order_id, product_id, product_name, quantity)
PK = (order_id, product_id)
FD: product_id → product_name      ← частичная зависимость
```

`product_name` зависит только от части PK (product_id), не от всего PK.

### Хорошо — разбить

```
order_lines(order_id, product_id, quantity)
products   (product_id, product_name)
```

> [!important] 2NF — формула
> Если PK составной и какой-то non-prime атрибут зависит только от ЧАСТИ PK — 2NF нарушено. Выноси этот атрибут с тем кусочком ключа в отдельную таблицу.

---

## 7. 3NF — Third Normal Form #normalization

**Правило:** 2NF + нет ТРАНЗИТИВНОЙ зависимости non-prime от PK.

Транзитивная: PK → A → B, где A non-prime.

### Плохо

```
employees(emp_id, name, dept_id, dept_name)
FD: emp_id  → dept_id
    dept_id → dept_name      ← транзитивная: emp_id → dept_id → dept_name
```

`dept_name` зависит от `dept_id`, а не напрямую от `emp_id`.

### Хорошо

```
employees  (emp_id, name, dept_id)
departments(dept_id, dept_name)
```

> [!tip] 3NF в одной фразе
> "Каждый non-key атрибут зависит от ключа, всего ключа и ни от чего, кроме ключа" (Codd).

### 3NF альтернативное определение
FD A → B нарушает 3NF, **если** не выполняется ни одно из:
1. A — super key, или
2. B — prime attribute (часть какого-то candidate key).

---

## 8. BCNF — Boyce-Codd Normal Form #normalization

**Правило:** для каждой нетривиальной FD `A → B`, A должен быть super key.

BCNF строже 3NF: 3NF позволял исключение, если B — prime. BCNF — нет.

### Плохо (3NF, но не BCNF)

```
classes(student_id, course, instructor)
FD: instructor → course           ← preceptor преподаёт ровно один курс
    student_id, course → instructor
PK: (student_id, course)
```

`instructor` не super key, но определяет `course`. 3NF разрешает (course — prime), BCNF — нет.

### Хорошо

```
class_instructor(instructor, course)
class_student   (student_id, instructor)
```

> [!warning] BCNF может терять FD
> При декомпозиции в BCNF иногда теряется зависимость, которую невозможно проверить без JOIN. Это компромисс — больше дробим, но не всегда сохраняем все FD.

> [!important] BCNF vs 3NF
> Все BCNF → 3NF. Не все 3NF → BCNF. На практике обычно нормализуют до 3NF, до BCNF — если есть аномалии, которые 3NF не убрал.

---

## 9. 4NF — Multi-valued dependencies

**MVD** A →→ B значит: "для каждого A набор связанных B не зависит от других атрибутов". #dbterm

### Плохо

```
employee_skills_languages(emp_id, skill, language)
emp_id =1, skills = {SQL, Python}, languages = {EN, RU}
```

→ строки: (1, SQL, EN), (1, SQL, RU), (1, Python, EN), (1, Python, RU). Декартово.

### Хорошо

```
employee_skills    (emp_id, skill)
employee_languages (emp_id, language)
```

4NF: BCNF + нет нетривиальных MVD, кроме случаев когда левая часть super key.

---

## 10. 5NF — Join Normal Form

Очень редко, обычно за пределами курса. Решает проблему, когда таблица не разбивается на две без потери, но разбивается на три.

> [!tip] На экзамене
> 1NF → 2NF → 3NF → BCNF — вот эти проверять. 4NF/5NF — упоминаются, но обычно не требуют декомпозиции.

---

## 11. Декомпозиция

При разбиении таблицы важны **два свойства**:

### 11.1 Lossless join decomposition

После разбиения и обратного JOIN-а получим **точно** исходные данные. Без потерь, без появления "лишних".

> [!important] Условие lossless
> Если разбиваем R на R1 и R2 по общему атрибуту X, то decomposition lossless ⇔ X — super key хотя бы одной из R1 или R2.

Пример lossy (плохой):
```
employees(emp_id, name, dept_id, dept_name)
   ↓ разбили без общего ключа
T1(emp_id, name)         T2(dept_id, dept_name)
```
Теряется связь между сотрудником и отделом.

### 11.2 Dependency preservation

Все FD из исходной таблицы можно проверить, не делая JOIN. Свойство хорошее, но достижимо не всегда.

| Подход | Lossless | Dependency-preserving |
|---|---|---|
| 3NF synthesis | да | да |
| BCNF decomposition | да | НЕ всегда |

> [!warning] BCNF может пожертвовать dependency preservation
> Это известная цена BCNF. На практике часто останавливаются на 3NF, чтобы сохранить FD.

---

## 12. Алгоритм нормализации (как делать на экзамене)

1. **Найди все FD.**
2. **Найди candidate keys** через closure.
3. **Проверь 1NF:** все атомарно?
4. **Проверь 2NF:** для каждого non-prime атрибута — зависит ли он только от части candidate key? Если да — выдели в отдельную таблицу.
5. **Проверь 3NF:** есть ли транзитивные `PK → A → B`? Если да — выдели `(A, B)`.
6. **Проверь BCNF:** для каждой FD `A → B` — A super key? Если нет — выдели `(A, B)`.
7. **Убедись lossless** на каждом шаге.

---

## 13. Полный пример декомпозиции

### Исходная таблица:
```
EMP_DEPT(emp_id, emp_name, dept_id, dept_name, manager_id, manager_name)

FDs:
emp_id    → emp_name, dept_id
dept_id   → dept_name, manager_id
manager_id → manager_name
```

### Шаг 1 — закрытие
- (emp_id)+ = {emp_id, emp_name, dept_id, dept_name, manager_id, manager_name} → super key.
- Candidate key = {emp_id}. PK выбран.

### Шаг 2 — 1NF
Все атрибуты атомарны → ОК.

### Шаг 3 — 2NF
PK не составной → 2NF выполнено автоматически.

### Шаг 4 — 3NF
Есть транзитивные:
- `emp_id → dept_id → dept_name` (нарушение).
- `emp_id → dept_id → manager_id → manager_name` (двойное).

Декомпозиция:
```
employees   (emp_id PK, emp_name, dept_id FK)
departments (dept_id PK, dept_name, manager_id FK)
managers    (manager_id PK, manager_name)
```

### Шаг 5 — BCNF
В каждой таблице FD идёт от PK → BCNF выполнено.

> [!success] Результат
> Из одной "тяжёлой" таблицы получили 3 чистых, без redundancy и аномалий.

---

## 14. Денормализация — обратное

В реальной жизни иногда **специально** нарушают 3NF ради скорости:
- Хранить агрегаты (`total_balance` в `customers`) — обновляется триггером.
- Хранить избыточные FK для быстрых JOIN-ов.
- Pre-joined таблицы для отчётов.

> [!warning] Когда денормализовать
> Только когда: 1) есть бенчмарк-доказательство необходимости, 2) обновления редкие, чтения частые, 3) есть механизм синхронизации (триггер, материализация).
> Иначе — нормализуй.

---

## 15. Часто на экзамене

> [!danger] Exam traps
> 1. **2NF имеет смысл только при составном PK.** Если PK один атрибут — сразу 2NF.
> 2. **3NF vs BCNF** — 3NF разрешает FD на prime атрибут, BCNF — нет.
> 3. **Lossless** требует, чтобы общий атрибут был super key хотя бы в одной части.
> 4. **MVD ≠ FD** — MVD это про "независимые наборы".
> 5. **Аномалии** — знать три (insert, update, delete).
> 6. **Closure** — обязательный навык: посчитать (X)+ по списку FD.

---

## 16. Mini-quiz

1. У таблицы `(A, B, C, D)` PK=(A, B), FD: `B → C`. Какая нормальная форма нарушена?
2. Что значит "X — super key"?
3. Чем отличается 3NF от BCNF? Приведи случай, когда 3NF выполнено, а BCNF нет.
4. Можно ли всегда привести таблицу к BCNF без потери FD?
5. Найди (A)+ при FD: A→B, B→C, C→D, AE→F.

> [!success] Если понял эту главу
> Ты умеешь считать closure FD, находить candidate keys, проверять и приводить таблицы к 1NF, 2NF, 3NF, BCNF. Это самый "математический" блок курса — стоит дороже всех на экзамене.
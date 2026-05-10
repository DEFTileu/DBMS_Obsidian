# 01 — Introduction to Database Systems

> Зачем эта тема: понять, **что такое БД**, чем она лучше обычных файлов, кто и как с ней работает. Это фундамент всего курса — без этой главы остальные не имеют смысла.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/22

---

## 1. Зачем вообще нужна база данных

Представь, что ты хранишь данные банка в обычных файлах: `customers.txt`, `accounts.txt`, `loans.txt`. Что пойдёт не так?

- **Дублирование данных** — адрес клиента лежит в трёх файлах, и при изменении надо править вручную.
- **Несогласованность** — в одном файле адрес обновили, в другом нет → данные противоречат друг другу.
- **Сложный доступ** — для каждого нового запроса надо писать отдельную программу.
- **Параллельный доступ** — два кассира одновременно списывают деньги со счёта → баланс ломается.
- **Безопасность** — каждый, у кого есть файл, видит ВСЁ.
- **Целостность** — никто не гарантирует, что баланс ≥ 0.

> [!abstract] Главная идея
> **DBMS** решает все эти проблемы: один контролируемый слой между приложением и данными.

---

## 2. Базовые термины

**DBMS (Database Management System)** — программа, которая управляет базой данных: хранит, защищает, обновляет, выдаёт по запросу. #abbreviation

**database** — структурированная коллекция связанных данных. #dbterm

**data** — сырые факты (число, строка, дата). #dbterm

**information** — обработанные данные с контекстом. #dbterm

**metadata** — данные о данных (структура, типы, ограничения). #dbterm

**schema** — описание структуры БД: какие таблицы, какие столбцы, какие связи. #dbterm

**instance** — текущее состояние данных в БД на конкретный момент времени. #dbterm

> [!tip] Schema vs instance
> **Schema** — это как класс в ООП (структура).
> **Instance** — это объект (конкретные значения сейчас).
> Schema меняется редко, instance — постоянно.

---

## 3. Файловая система vs DBMS

| Критерий | File system | DBMS |
|---|---|---|
| Дублирование данных | высокое | низкое (нормализация) |
| Согласованность | приложение само следит | гарантирует DBMS |
| Параллельный доступ | трудно | через transactions |
| Целостность | через код | через constraints |
| Безопасность | права на файл | роли + права на таблицы/столбцы |
| Гибкость запросов | свой код для каждого | универсальный SQL |
| Восстановление после сбоя | нет | есть (logs, backup) |

> [!warning] Ловушка
> "Я просто положу JSON в файл" — норм для прототипа, но как только появляются параллельные пользователи и важные данные, надо переходить на DBMS.

---

## 4. Уровни абстракции данных

DBMS прячет от пользователя физические детали. Уровней три:

1. **Physical level** — как байты лежат на диске, какие индексы, какая страница.
2. **Logical level** — какие таблицы, какие столбцы, какие связи. Это то, что описывает schema.
3. **View level** — что видит конкретный пользователь (часть данных, агрегаты). Может быть несколько views.

> [!important] Data independence
> **Physical data independence** — можно менять физическое хранение, не трогая логику.
> **Logical data independence** — можно расширять schema, не трогая старые приложения.
> Главная цель — изоляция приложения от деталей хранения.

---

## 5. Языки баз данных

DBMS говорит на нескольких "под-языках" SQL.

**DDL (Data Definition Language)** — описывает структуру: `CREATE`, `ALTER`, `DROP`, `TRUNCATE`. #abbreviation

**DML (Data Manipulation Language)** — работает с данными: `SELECT`, `INSERT`, `UPDATE`, `DELETE`. #abbreviation

**DCL (Data Control Language)** — права: `GRANT`, `REVOKE`. #abbreviation

**TCL (Transaction Control Language)** — управление транзакциями: `COMMIT`, `ROLLBACK`, `SAVEPOINT`. #abbreviation

> [!tip] Memory hook — D-D-D-T
> **D**efinition · **D**ata · **D**ata-control · **T**ransaction

```sql
-- DDL
CREATE TABLE customers (id INT PRIMARY KEY, name VARCHAR(100));
ALTER TABLE customers ADD COLUMN email VARCHAR(255);
DROP TABLE customers;

-- DML
INSERT INTO customers VALUES (1, 'Aigerim');
SELECT * FROM customers WHERE id = 1;
UPDATE customers SET name = 'Aigerim K.' WHERE id = 1;
DELETE FROM customers WHERE id = 1;

-- DCL
GRANT SELECT ON customers TO some_user;
REVOKE SELECT ON customers FROM some_user;

-- TCL
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;
-- или ROLLBACK;
```

`CREATE TABLE name (col TYPE …);` #sqlcommand
Создаёт новую таблицу.

`ALTER TABLE name ADD/DROP/MODIFY …;` #sqlcommand
Меняет существующую таблицу.

`DROP TABLE name;` #sqlcommand
Удаляет таблицу полностью (вместе с данными и структурой).

`GRANT priv ON object TO user;` #sqlcommand
Выдаёт право (например, `SELECT`) пользователю.

> [!danger] Exam trap — DROP vs DELETE vs TRUNCATE
> - `DROP TABLE` → удаляет ТАБЛИЦУ (структуру + данные).
> - `DELETE FROM table` → удаляет СТРОКИ, можно с `WHERE`. DML, можно откатить.
> - `TRUNCATE TABLE` → удаляет ВСЕ строки разом, быстро, обычно не откатить (DDL в большинстве СУБД).

---

## 6. Архитектура DBMS

### 6.1 Двухуровневая (2-tier)

`Client app` ↔ `DBMS server`

Клиент сам шлёт SQL-запросы серверу. Простая схема, но плохо масштабируется и опасно (логика на клиенте).

### 6.2 Трёхуровневая (3-tier)

`Client (UI)` ↔ `Application server (logic)` ↔ `DBMS server`

Современный стандарт. Приложение между UI и БД отвечает за бизнес-логику и безопасность. Это то, что используют все веб-приложения.

> [!tip] Почему 3-tier лучше
> - UI меняется без перекомпиляции серверной логики.
> - Бизнес-правила централизованы.
> - БД доступна только серверу приложений → меньше attack surface.

---

## 7. Компоненты DBMS

Внутри сервера БД работает несколько подсистем:

| Компонент | Роль |
|---|---|
| **Query processor** | парсит SQL, строит и оптимизирует план выполнения |
| **Storage manager** | работает с диском, файлами, страницами |
| **Buffer manager** | держит часто используемые страницы в памяти |
| **Transaction manager** | следит за ACID, locking, isolation |
| **Recovery manager** | восстанавливает БД после сбоя через log |
| **Authorization manager** | проверяет права на каждое действие |

> [!abstract] В одной фразе
> Query processor решает **что делать**, storage manager — **где взять данные**, transaction manager — **как сделать безопасно**, recovery — **что делать если упало**.

---

## 8. Пользователи БД

| Роль | Что делает |
|---|---|
| **Naive user** | работает через готовое приложение (кассир, оператор) |
| **Application programmer** | пишет приложение, которое ходит в БД |
| **Sophisticated user** | сам пишет SQL для аналитики |
| **DBA (Database Administrator)** | проектирует БД, управляет правами, бэкапами, performance |

**DBA (Database Administrator)** — главный человек по БД: создаёт схему, выдаёт права, настраивает backup, мониторит performance. #abbreviation

---

## 9. Модели данных

Модель данных — способ описания структуры БД. Основные:

- **Relational** — таблицы, строки, столбцы (то, что мы изучаем). Стандарт индустрии.
- **Entity-Relationship (ER)** — для проектирования (Chapter 6).
- **Object-based** — объекты, классы, наследование.
- **Semi-structured** — JSON, XML — гибкая схема.
- **Hierarchical** (исторический) — дерево.
- **Network** (исторический) — граф через указатели.

> [!important] Why relational won
> Простая, математически обоснованная (set theory + relational algebra), декларативный язык (SQL), независимость от физического хранения.

---

## 10. Жизненный цикл проектирования БД

1. **Requirements analysis** — что бизнес хочет хранить и узнавать.
2. **Conceptual design** — рисуем **ERD** (Chapter 6).
3. **Logical design** — переводим ERD в таблицы, нормализуем (Chapter 7).
4. **Physical design** — выбираем индексы, partitioning, типы хранения.
5. **Implementation** — пишем DDL, заливаем данные.
6. **Maintenance** — мониторинг, оптимизация, изменение схемы.

> [!tip] Memory hook — RCLPIM
> **R**equirements → **C**onceptual → **L**ogical → **P**hysical → **I**mplementation → **M**aintenance.

---

## 11. Преимущества DBMS — итог

- **Контроль избыточности** (через нормализацию).
- **Целостность** (через constraints).
- **Безопасность** (через GRANT/REVOKE).
- **Параллельность** (через транзакции).
- **Восстановление** (через WAL и backup).
- **Декларативные запросы** (SQL).
- **Independence** (логика приложения не зависит от хранения).

---

## 12. Недостатки DBMS — честно

- **Сложность** — DBMS большие, требуют DBA.
- **Стоимость** — лицензии (Oracle, MS SQL), железо, обучение.
- **Overhead** — для крошечных приложений может быть избыточен.
- **Vendor lock-in** — миграция между СУБД дорогая.

> [!warning] Когда DBMS не нужен
> Простой конфиг, одиночный пользователь без параллелизма, embedded-сценарий — иногда хватит SQLite или просто файла.

---

## 13. Часто на экзамене

> [!danger] Exam trap-ы по этой главе
> 1. **DDL vs DML vs DCL vs TCL** — путают `TRUNCATE` (DDL) и `DELETE` (DML).
> 2. **Schema vs instance** — schema это структура, instance это текущие данные.
> 3. **Physical vs logical data independence** — physical = смена хранения, logical = смена структуры.
> 4. **2-tier vs 3-tier** — 3-tier добавляет application server между клиентом и БД.
> 5. **DBA** — обязательно знать, чем отличается от обычного пользователя.

---

## 14. Mini-quiz для самопроверки

1. Чем отличается `DROP TABLE` от `DELETE FROM`?
2. К какому языку относится `GRANT`?
3. Что такое **physical data independence**?
4. Что хранится на logical level и что на view level?
5. Какие 6 проблем решает DBMS по сравнению с файлами?

> [!success] Если понял эту главу
> Ты знаешь, **что такое DBMS**, **зачем он нужен**, **из чего состоит** и **какими языками** с ним общаются. Это база, на которой будет стоять весь курс.
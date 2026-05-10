# 14 — Transactions

> Зачем эта тема: **транзакция — это контракт DBMS** перед приложением. ACID, isolation levels, locking, deadlock, recovery — это ВСЁ почти всегда на финале. Хорошее знание этой главы вытягивает оценку.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/35

---

## 1. Что такое транзакция

**transaction** — последовательность операций над БД, которая выполняется как **единое целое**: либо всё, либо ничего. #dbterm

```sql
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;
COMMIT;
```

Если на втором UPDATE упадёт сервер — DBMS откатит первый.

> [!abstract] Главная идея
> БД сама по себе ничем не лучше файла. Что делает её **базой** — это гарантия атомарности и согласованности через транзакции.

---

## 2. ACID

**ACID** — базовый набор свойств транзакции. #abbreviation

| Буква | Свойство | Что значит |
|---|---|---|
| **A** | **Atomicity** | всё или ничего |
| **C** | **Consistency** | БД всегда в валидном состоянии (constraints соблюдены) |
| **I** | **Isolation** | параллельные транзакции не мешают друг другу |
| **D** | **Durability** | после COMMIT данные не пропадут даже при crash |

### 2.1 Atomicity
Если транзакция упала — откат всех изменений. Реализация: undo log.

### 2.2 Consistency
До и после транзакции все constraints (FK, CHECK) выполняются. Сама транзакция может временно нарушать в середине.

### 2.3 Isolation
Параллельные транзакции "не видят" друг друга, как будто выполняются по очереди (см. isolation levels).

### 2.4 Durability
Зафиксированные данные сохранены, даже если сразу выключить питание. Реализация: WAL + force-at-commit.

> [!tip] Memory hook — ACID
> **A**ll-or-nothing → **C**onsistent state → **I**solated → **D**urable.

---

## 3. Состояния транзакции

```
[active] → [partially committed] → [committed]
   ↓                ↓
[failed] ──────→ [aborted]
```

| Состояние | Что |
|---|---|
| **Active** | выполняется |
| **Partially committed** | последняя операция выполнена, но COMMIT не дописан в WAL |
| **Committed** | WAL записан → точка не возврата |
| **Failed** | ошибка, откатывается |
| **Aborted** | откатилась полностью |

---

## 4. TCL — управление транзакциями в SQL

```sql
BEGIN;                    -- или START TRANSACTION
UPDATE accounts ...;
SAVEPOINT s1;
UPDATE customers ...;
ROLLBACK TO SAVEPOINT s1;  -- откатить только до s1
UPDATE customers ...;
COMMIT;                    -- зафиксировать всё
```

`BEGIN` / `START TRANSACTION` #sqlcommand — открыть транзакцию.

`COMMIT` #sqlcommand — зафиксировать.

`ROLLBACK` #sqlcommand — откатить.

`SAVEPOINT name` #sqlcommand — поставить отметку.

`ROLLBACK TO SAVEPOINT name` #sqlcommand — откатить до отметки, оставить транзакцию открытой.

> [!warning] Autocommit
> По умолчанию во многих драйверах каждая команда = своя транзакция. Чтобы атомарно — обязательно `BEGIN…COMMIT` или `with transaction:`.

---

## 5. Concurrency проблемы

При параллельных транзакциях БЕЗ изоляции возникают аномалии:

### 5.1 Dirty read
T1 изменила, T2 прочитала, T1 откатилась → T2 прочитала несуществующее.

```
T1: UPDATE balance = 200    (не commit)
T2: SELECT balance → 200    ← dirty
T1: ROLLBACK                ← T2 видела фантом
```

### 5.2 Non-repeatable read
T1 читает дважды одну строку, между чтениями T2 её изменила и закоммитила. T1 видит разные значения.

### 5.3 Phantom read
T1 делает `SELECT WHERE …`, T2 вставляет новую строку, удовлетворяющую условию. T1 повторяет → видит "появившиеся" строки.

### 5.4 Lost update
Две транзакции читают, обновляют и пишут — одна перезаписывает изменения другой.

```
T1: read balance (100) → write 100+50
T2: read balance (100) → write 100+30
ИТОГ: 130, должно было быть 180.
```

> [!important] Запомнить названия
> Dirty / non-repeatable / phantom / lost update — это четыре классические аномалии. Финал любит спрашивать: "при каком isolation возникает X?".

---

## 6. Isolation levels

Стандарт SQL определяет 4 уровня:

| Уровень | Dirty read | Non-repeatable | Phantom |
|---|---|---|---|
| **Read uncommitted** | возможно | возможно | возможно |
| **Read committed** | НЕТ | возможно | возможно |
| **Repeatable read** | НЕТ | НЕТ | возможно* |
| **Serializable** | НЕТ | НЕТ | НЕТ |

\* В Postgres и MySQL InnoDB Repeatable Read часто исключает phantom через MVCC + range lock.

### 6.1 Установка
```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- или внутри транзакции
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

### 6.2 Какой уровень выбрать

| Уровень | Когда |
|---|---|
| **Read uncommitted** | почти никогда (грязные данные) |
| **Read committed** | дефолт в Postgres, ОК для большинства |
| **Repeatable read** | финансовые операции, отчёты |
| **Serializable** | максимальная безопасность, но медленнее |

> [!tip] Postgres MVCC + Serializable
> В Postgres Serializable реализован через SSI (Serializable Snapshot Isolation) — без локов, через детектирование циклов. Очень элегантно.

---

## 7. Locking — реализация изоляции

### 7.1 Виды локов

| Lock | Что блокирует |
|---|---|
| **Shared (S)** | разрешает чтение другим, запрет записи |
| **Exclusive (X)** | запрет любого доступа другим |
| **Intent (IS, IX)** | флаг, что в дочерних объектах будут локи |

### 7.2 Гранулярность

- Database-level
- Table-level
- Page-level
- Row-level (стандарт)
- **Lock escalation** — мелкие локи могут "укрупняться" в табличный.

### 7.3 Two-phase locking (2PL)

**2PL**: транзакция сначала только **набирает** локи (growing phase), потом только **отпускает** (shrinking phase).

```
T: lock A, lock B, work, work, unlock A, unlock B  ← правильный 2PL
T: lock A, work, unlock A, lock B, work, unlock B  ← НЕ 2PL (можно нарушить serializability)
```

**Strict 2PL**: все X-локи держатся до COMMIT/ROLLBACK. Стандарт.

> [!important] 2PL → serializability
> Если все транзакции следуют 2PL — расписание гарантированно serializable.

---

## 8. Deadlock

**deadlock** — две (или больше) транзакции блокируют друг друга, никто не может продолжить. #dbterm

```
T1: lock A → ждёт B
T2: lock B → ждёт A
```

### 8.1 Обнаружение

DBMS строит **wait-for graph**: T1 → T2 если T1 ждёт T2. Если есть цикл → deadlock.

### 8.2 Разрешение

Выбирается **жертва** (обычно самая молодая или с наименьшей работой), её транзакция откатывается. Приложение должно retry.

```sql
ERROR: deadlock detected
```

### 8.3 Профилактика

- Всегда брать локи в одинаковом порядке (например, по `id ASC`).
- Минимизировать длительность транзакций.
- Использовать оптимистичные стратегии (MVCC, `SELECT FOR UPDATE NOWAIT`).
- Timeout-ы.

> [!warning] Retry — обязательно
> Любая транзакция в высоконагруженной системе может встретить deadlock. Код должен ловить ошибку и повторять.

---

## 9. Optimistic vs Pessimistic concurrency

| | Pessimistic (locking) | Optimistic |
|---|---|---|
| Идея | блокировать заранее | работать без локов, проверить в конце |
| Цена | блокировки = ожидание | abort + retry при конфликте |
| Подходит | high contention | low contention |
| Реализация | 2PL | MVCC, version numbers |

> [!tip] Postgres
> Использует MVCC (optimistic для чтений) + строковые локи на UPDATE/DELETE. Лучшее из двух миров для большинства workload.

---

## 10. MVCC

**MVCC (Multi-Version Concurrency Control)** — каждая транзакция видит снимок данных на момент её начала. Старые версии хранятся, пока их видят активные. #abbreviation

Плюс: чтение не блокирует запись, и наоборот.
Минус: bloat — нужно vacuum.

```
T1 (start at time 100): видит версию tuple на момент 100
T2 (start at time 110, обновляет tuple): создаёт новую версию
T1 продолжает видеть старую версию → нет блокировки.
```

> [!important] Зачем VACUUM в Postgres
> Из-за MVCC после UPDATE/DELETE остаются "мёртвые" tuple. Без VACUUM таблица распухает, индексы становятся неэффективны.

---

## 11. Recovery — восстановление после crash

### 11.1 Зачем

Crash может случиться:
- В середине транзакции — нужно откатить.
- После COMMIT — нужно гарантировать сохранность (Durability).

### 11.2 Write-Ahead Log (WAL)

**WAL** — все изменения сначала пишутся в журнал, потом применяются к данным. #abbreviation

Правило WAL:
- **Перед** записью изменения tuple на диск, запись в log должна быть на диске.
- **Перед** COMMIT, log-запись о коммите должна быть на диске.

> [!important] Sequential write
> Лог пишется последовательно (быстро), а данные — в случайные блоки (медленно). WAL даёт durability дешёво.

### 11.3 Undo / Redo

- **Undo log** — старые значения, чтобы откатить незавершённые транзакции при recovery.
- **Redo log** — новые значения, чтобы повторно применить committed транзакции, если их данные ещё не на диске.

### 11.4 Алгоритм recovery (упрощённо)

1. Найти последний **checkpoint**.
2. **Redo phase**: пройти лог от checkpoint вперёд, применить изменения committed транзакций.
3. **Undo phase**: откатить транзакции, не успевшие COMMIT (по undo log).

### 11.5 Checkpoint

**checkpoint** — момент, когда DBMS гарантирует: все dirty pages до этого момента сброшены на диск. Recovery начинается с последнего checkpoint, не с начала времён. #dbterm

> [!tip] ARIES
> Industry standard алгоритм recovery: ARIES (Algorithm for Recovery and Isolation Exploiting Semantics). Использует WAL + undo + redo + LSN.

---

## 12. Backup и DR

| Тип | Что |
|---|---|
| **Full backup** | копия всех данных |
| **Incremental** | только изменения с последнего full |
| **PITR (Point-in-time recovery)** | full + WAL → откат к любому моменту |

> [!warning] Backup невозможен без WAL
> Snapshot БД "как есть" может быть несогласован (часть страниц старые, часть новые). Нужен WAL до snapshot, чтобы recovery согласовал.

> [!danger] DR-план должен быть проверен
> Бэкап без проверки восстановления = бэкапа нет. Минимум раз в квартал — учебное восстановление в staging.

---

## 13. Distributed transactions — кратко

В распределённой системе транзакция может затрагивать несколько узлов. Проблема: как coordinated commit?

### 13.1 Two-phase commit (2PC)

1. **Prepare** — координатор спрашивает: "готовы commit?"
2. Все отвечают yes/no.
3. Если все yes → координатор шлёт COMMIT, иначе ROLLBACK.

Минус: блокирующий, при падении координатора участники зависают.

### 13.2 Saga pattern

Длинная распределённая транзакция = последовательность локальных транзакций + компенсирующих (rollback) операций. Использует eventual consistency.

> [!tip] CAP theorem
> В распределённой системе можно одновременно иметь только 2 из 3: **C**onsistency, **A**vailability, **P**artition tolerance.

---

## 14. Сериализация и serializable schedule

**Schedule** — порядок операций нескольких транзакций.
**Serial schedule** — транзакции выполняются строго одна за другой.
**Serializable schedule** — параллельный, но эквивалентный какому-то serial.

### 14.1 Conflict serializability

Две операции конфликтуют, если:
- они из разных транзакций,
- работают с одним и тем же объектом,
- хотя бы одна — write.

Schedule conflict-serializable, если можно переставить неконфликтующие операции и получить serial schedule.

### 14.2 Precedence graph

T1 → T2, если есть конфликт, где операция T1 предшествует операции T2.
Если граф ацикличный → conflict-serializable.

> [!important] На экзамене
> Дано schedule → нарисуй precedence graph → проверь циклы → conflict-serializable или нет.

---

## 15. Часто на экзамене

> [!danger] Exam traps
> 1. **ACID** — все четыре буквы и что они гарантируют.
> 2. **Isolation level vs anomaly** — таблица "что разрешено на каком уровне".
> 3. **2PL** — определение и почему обеспечивает serializability.
> 4. **Deadlock** — как обнаруживается и разрешается.
> 5. **MVCC** — суть и зачем VACUUM.
> 6. **WAL** — sequential write, redo/undo.
> 7. **Conflict serializability** — precedence graph.
> 8. **2PC** — для распределённых транзакций.

---

## 16. Mini-quiz

1. На каком isolation level возможны phantom reads?
2. Что произойдёт при `ROLLBACK TO SAVEPOINT s1` после нескольких UPDATE-ов?
3. Как DBMS обнаруживает deadlock?
4. Почему WAL быстрее, чем "writing to data files"?
5. Что такое two-phase locking? Зачем нужен strict 2PL?

> [!success] Если понял эту главу
> Ты понимаешь, **почему БД называется БД**: ACID, isolation, recovery, locking. Это смысловой фундамент всего курса. Без транзакций — это просто файл с структурой.

---

## 17. Главный итог курса

> [!abstract] Что мы прошли за курс
> 1. **Что** хранить (relational model, ER, normalization).
> 2. **Как** запрашивать (SQL: basic → intermediate → advanced).
> 3. **Где** хранится (storage, indexing).
> 4. **Как быстро** (query processing, optimization).
> 5. **Безопасно ли** (transactions, ACID, recovery).
>
> Это полный круг от пользователя до диска и обратно.
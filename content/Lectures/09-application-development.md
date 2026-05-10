# 09 — Application Development with Databases

> Зачем эта тема: БД редко используется в одиночку — она живёт за веб-приложением. Эта глава показывает, **как программа общается с БД**, как защищаться от **SQL injection** и какие приёмы влияют на производительность.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/30

---

## 1. Архитектура приложения с БД

### 1.1 Типичный 3-tier

```
[Browser]  ←→  [Application server]  ←→  [DBMS]
   UI            бизнес-логика, API       данные
```

- Браузер отправляет HTTP-запросы → сервер.
- Сервер читает/пишет в БД через драйвер.
- БД защищена тем, что доступна только серверу.

### 1.2 Стэк

| Слой | Примеры |
|---|---|
| Frontend | React, Vue |
| Backend | Node.js, Django, Spring, Laravel |
| Database driver | psycopg2, JDBC, ODBC, pg |
| DBMS | PostgreSQL, MySQL, Oracle |

> [!important] Граница доверия
> **Никогда** не пускай браузер напрямую в БД. Всегда между ними сервер с авторизацией и валидацией.

---

## 2. API уровни — как программа говорит с БД

### 2.1 ODBC

**ODBC (Open Database Connectivity)** — кросс-платформенный API, написанный на C, единый интерфейс к разным СУБД. #abbreviation

### 2.2 JDBC

**JDBC (Java Database Connectivity)** — Java-аналог ODBC. #abbreviation

```java
Connection conn = DriverManager.getConnection(url, user, pass);
PreparedStatement st = conn.prepareStatement("SELECT * FROM customers WHERE id = ?");
st.setInt(1, customerId);
ResultSet rs = st.executeQuery();
while (rs.next()) {
    System.out.println(rs.getString("name"));
}
```

### 2.3 Embedded SQL

SQL прямо в коде, препроцессор переводит в вызовы. Используется в COBOL, C для legacy.

### 2.4 Native drivers

В каждом языке свой:
- Python: `psycopg2`, `asyncpg`.
- Node.js: `pg`, `mysql2`.
- Go: `pgx`, `database/sql`.

### 2.5 Dynamic SQL

SQL формируется во время выполнения. Гибко, но опасно (SQL injection!) — поэтому почти всегда заменяется prepared statements.

> [!warning] Dynamic SQL без подготовки
> `query = "SELECT * FROM users WHERE name = '" + input + "'"` — открытая дверь для injection.

---

## 3. SQL Injection — главная угроза

**SQL injection** — атака, при которой злоумышленник внедряет SQL-код через пользовательский ввод. #dbterm

### 3.1 Классический пример

Уязвимый код (псевдо):
```python
query = f"SELECT * FROM users WHERE login = '{user}' AND password = '{pwd}'"
```

Если злоумышленник вводит логин: `admin' --`
```sql
SELECT * FROM users WHERE login = 'admin' --' AND password = '...'
```
`--` — комментарий, всё после игнорируется. Залог — мимо проверки пароля.

### 3.2 UNION-based

Если уязвим SELECT, можно через `UNION` достать другие данные:
```
input: ' UNION SELECT credit_card_no FROM payments --
```

### 3.3 Blind SQL injection

Когда нет вывода SQL ошибок, но есть разница в поведении (HTTP 200 / 500):
```
input: ' OR (SELECT SUBSTRING(password,1,1) FROM users WHERE id=1) = 'a' --
```

### 3.4 Защита — Prepared Statements

```python
# psycopg2
cur.execute("SELECT * FROM users WHERE login = %s AND password = %s", (user, pwd))
```

```java
// JDBC
PreparedStatement st = conn.prepareStatement("SELECT * FROM users WHERE login = ? AND password = ?");
st.setString(1, user);
st.setString(2, pwd);
```

> [!danger] ГЛАВНОЕ правило безопасности
> **НИКОГДА** не склеивай user input в SQL-строку. **ВСЕГДА** используй prepared statements (`?` или `:param`). Это не вопрос "стиля" — это вопрос безопасности.

### 3.5 Дополнительные слои защиты

- **Принцип наименьших привилегий** — у app-юзера нет `DROP TABLE`.
- **Validate input** — длина, формат, тип.
- **WAF** (web application firewall).
- **Stored procedures** — пользователь вызывает только `CALL transfer(...)`.
- **ORM** (под капотом prepared statements).

---

## 4. ORM — Object-Relational Mapping

**ORM** — слой, отображающий объекты языка на таблицы БД. #abbreviation

```python
# Django
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

# Использование
c = Customer.objects.get(id=1)
c.name = 'Aigerim'
c.save()

Customer.objects.filter(name__startswith='A').order_by('-id')
```

| Плюсы | Минусы |
|---|---|
| Без ручного SQL для простых случаев | "магия", сложно понять, какой SQL выполняется |
| Защита от injection (под капотом prepared) | N+1 проблема — частая ловушка |
| Миграции схемы | плохо ложится на сложные запросы |

### 4.1 Проблема N+1

```python
# 1 запрос на Order
orders = Order.objects.all()
for o in orders:
    print(o.customer.name)   # N запросов на каждого клиента
```

Решение: eager loading.
```python
Order.objects.select_related('customer')   # 1 JOIN запрос
```

> [!warning] N+1 — главный убийца производительности
> Видишь "100 запросов на одну страницу" — это почти всегда N+1. `select_related`, `prefetch_related`, `JOIN`.

---

## 5. Connection pool

Открыть TCP-соединение к БД дорого. Решение — **пул**:
- Программа держит N открытых соединений.
- На запрос — берёт из пула.
- После — возвращает.

```
[App threads] ← → [Pool of 20 connections] ← → [DBMS]
```

Параметры:
- `min_idle` / `max_size` — границы пула.
- `idle_timeout` — закрывать неактивные.
- `max_lifetime` — пересоздавать раз в час.

> [!important] Без pool — деградация под нагрузкой
> Каждый HTTP-запрос открывает новое TCP + аутентификацию (~10ms+). При 1000 RPS это убийственно.

> [!tip] PgBouncer / pgpool
> Для Postgres часто ставят отдельный пулер между приложением и БД, чтобы пул был общим для всех инстансов backend-а.

---

## 6. Транзакции из приложения

```python
import psycopg2

with psycopg2.connect(DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (1000, 1))
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (1000, 2))
    # commit при выходе из with, rollback при exception
```

> [!important] Транзакция = единица атомарности
> Все изменения, которые должны произойти "вместе или никак", оборачивай в одну транзакцию. По умолчанию во многих драйверах включён autocommit — каждая команда = своя транзакция; явно выключай.

---

## 7. Sessions, cookies, аутентификация

### 7.1 Стандартный flow

1. Логин → сервер проверяет пароль (хеш!) в БД.
2. Создаёт **session** или **JWT**, отдаёт клиенту в cookie.
3. На следующих запросах — передаёт cookie → сервер проверяет → знает кто это.

### 7.2 Хранение паролей

- **НИКОГДА** не plain text.
- **НИКОГДА** не MD5/SHA1 без соли.
- Только **bcrypt / argon2** с солью и rounds.

```python
from passlib.hash import bcrypt
hashed = bcrypt.hash(password)
bcrypt.verify(input_password, hashed)
```

> [!danger] Pasword leak
> Утечка БД с правильно хешированными паролями — неприятно, но восстановить почти нечего. Утечка с plain text — катастрофа.

### 7.3 CSRF / XSS / другие OWASP

| Атака | Защита |
|---|---|
| **SQL injection** | prepared statements |
| **XSS** | escape HTML на выводе, CSP |
| **CSRF** | anti-CSRF token, SameSite cookies |
| **IDOR** | проверка авторизации на КАЖДЫЙ доступ |
| **Mass assignment** | whitelist полей при INSERT/UPDATE |

---

## 8. Веб-производительность и БД

### 8.1 Каскад действий

```
HTTP request →
  parse →
  AuthN/AuthZ →
  DB query (часто несколько) →
  business logic →
  serialize JSON →
  send response
```

Узкое место чаще всего — **БД**. Меры:

### 8.2 Индексы (см. ch12)
Если фильтр по столбцу — нужен индекс.

### 8.3 Pagination
```sql
LIMIT 20 OFFSET 1000;
```
Для больших offset медленно. Используй keyset:
```sql
WHERE id > :last_seen_id ORDER BY id LIMIT 20;
```

### 8.4 Cache
```
Read: cache → если miss → БД → положить в cache.
```
Слой: in-process (LRU), отдельный (Redis), CDN (для статики).

> [!warning] Cache invalidation
> "Two hardest things in CS: cache invalidation and naming." — освободил кеш не вовремя → пользователь видит устаревшие данные. Стратегии: TTL, write-through, event-based.

### 8.5 Запросы только нужного
- `SELECT *` — никогда. Только нужные столбцы.
- `WHERE` обязательно. Ограничивать выборку.
- `LIMIT` обязательно для веба.

### 8.6 Read replicas

Для масштабирования чтения — реплики. Чтение → реплика, запись → master.

---

## 9. Migrations

**migration** — версия изменений схемы БД, применяемая по порядку и обратимая. #dbterm

```
V001__create_customers.sql
V002__add_email_to_customers.sql
V003__create_index_email.sql
```

Инструменты: Flyway (Java), Alembic (Python), Django migrations, Knex (Node).

> [!important] Никогда не правь "руками"
> Изменения схемы — только через миграции. Иначе на staging и prod разойдётся, и через год никто не вспомнит, что и когда поменяли.

> [!tip] Backwards-compatible миграции
> 1. Добавить новый столбец `nullable`.
> 2. Деплой кода, который пишет и в новый, и в старый.
> 3. Backfill старых данных.
> 4. Сделать `NOT NULL`.
> 5. Удалить старый столбец в следующем релизе.
>
> Это позволяет деплоить без downtime.

---

## 10. Web architecture: SQL injection example end-to-end

Уязвимый поиск:
```php
$q = $_GET['q'];
$sql = "SELECT * FROM products WHERE name LIKE '%$q%'";
```

Атакующий: `?q=' UNION SELECT credit_card FROM payments --`

```sql
SELECT * FROM products WHERE name LIKE '%' UNION SELECT credit_card FROM payments --%';
```

Защищённый код:
```php
$stmt = $pdo->prepare("SELECT * FROM products WHERE name LIKE ?");
$stmt->execute(["%$q%"]);   // % — данные, не SQL
```

> [!success] Главный takeaway
> Любой user input → через prepared statement. Точка.

---

## 11. Best practices — checklist

- ✅ Prepared statements ВЕЗДЕ.
- ✅ Connection pool настроен.
- ✅ Транзакции с `BEGIN…COMMIT/ROLLBACK`.
- ✅ Индексы на часто фильтруемые столбцы.
- ✅ `SELECT` только нужных столбцов.
- ✅ Pagination keyset для больших таблиц.
- ✅ Пароли через bcrypt/argon2.
- ✅ App-юзер БД минимальные права (`SELECT/INSERT/UPDATE/DELETE` на таблицы — НЕ `DROP`).
- ✅ Backup и DR-план.
- ✅ Migrations через инструмент, не руками.
- ✅ Логирование медленных запросов.

---

## 12. Часто на экзамене

> [!danger] Exam traps
> 1. **SQL injection** — пример атаки и защита через prepared.
> 2. **JDBC vs ODBC** — JDBC для Java, ODBC кросс-платформенный (C).
> 3. **PreparedStatement** vs `Statement` в JDBC.
> 4. **N+1 проблема** в ORM.
> 5. **Stateless 3-tier** — клиент → app server → DBMS.
> 6. **Connection pool** — зачем и какие параметры.
> 7. **Хранение пароля** — bcrypt/argon2 + salt.

---

## 13. Mini-quiz

1. Почему нельзя `query = "... WHERE x = '" + user_input + "'"`?
2. Что произойдёт без connection pool при 1000 RPS?
3. В чём отличие `Statement` от `PreparedStatement` в JDBC?
4. Что такое N+1 в ORM и как с ним бороться?
5. Почему MD5 не годится для хранения паролей?

> [!success] Если понял эту главу
> Ты понимаешь, **как код безопасно работает с БД**, защищается от injection, использует пулы и транзакции, и какие пункты обязательны на проде. Это пересечение DBMS и веб-разработки — половина finals по этой главе именно тут.
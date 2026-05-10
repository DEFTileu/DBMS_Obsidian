# 13 — Query Processing & Optimization

> Зачем эта тема: DBMS получает SQL → решает, **как именно** его выполнить. Эта глава — про путь от текста запроса к плану выполнения, про алгоритмы JOIN-ов и про оптимизатор. На финале это объединённый блок ch15+16.

> [!tip] 🎯 Практический квиз
> 30 вопросов с ответами и объяснениями для самопроверки → https://sdu.javazhan.tech/questions/7/categories/34

---

## 1. Этапы обработки запроса

```
SQL text
   ↓ Parser           — синтаксис, имена существуют?
Parse tree
   ↓ Translator       — в реляционную алгебру
Logical plan
   ↓ Optimizer        — выбор лучшего физического плана
Physical plan
   ↓ Execution engine — операторы выполняются
Result
```

**parser** — переводит SQL в синтаксическое дерево. #dbterm

**query optimizer** — выбирает наилучший план выполнения. #dbterm

**execution engine** — выполняет операторы плана. #dbterm

---

## 2. Parser

Делает три вещи:
1. **Лексер** — разбивает текст на токены (`SELECT`, `FROM`, `t1`, …).
2. **Парсер** — строит синтаксическое дерево.
3. **Резолвер имён** — проверяет, что таблицы и столбцы существуют, доступны пользователю.

Если что-то не так — `SQL syntax error` / `relation "x" does not exist`.

---

## 3. Translator → Реляционная алгебра

```sql
SELECT name FROM employees WHERE salary > 1000;
```
переводится в:
```
π_name (σ_salary>1000 (employees))
```

Это **логический план** — что нужно сделать, без указания КАК.

> [!tip] См. ch2
> Все операторы (σ, π, ⋈, ∪, −) тут пригодятся.

---

## 4. Equivalence rules

Оптимизатор использует правила эквивалентности — две формулы дают одинаковый результат, но одна выполняется быстрее.

### Примеры

1. **Selection commutativity:** σ_A(σ_B(R)) = σ_B(σ_A(R))
2. **Selection cascade:** σ_A∧B(R) = σ_A(σ_B(R))
3. **Pushdown selection через join:** σ_A(R ⋈ S) = σ_A(R) ⋈ S, если A только из R
4. **Join commutative:** R ⋈ S = S ⋈ R
5. **Join associative:** (R ⋈ S) ⋈ T = R ⋈ (S ⋈ T)
6. **Projection cascade**: π_A(π_B(R)) = π_A(R), если A ⊆ B

> [!important] Selection pushdown
> Главный приём: **тащить σ как можно глубже** — фильтровать на источнике, чтобы JOIN работал с меньшими данными.

---

## 5. Физический план

Оптимизатор выбирает **физические операторы** — конкретные алгоритмы:

| Логический | Физические варианты |
|---|---|
| Selection | seq scan, index scan, index-only scan, bitmap scan |
| Projection | inline (без стоимости) |
| Join | nested-loop, sort-merge, hash join |
| GROUP BY | sort, hash |
| ORDER BY | sort, использовать индекс |

EXPLAIN покажет физический план:
```
Seq Scan on employees  (cost=0.00..1234.00 rows=1000 width=64)
  Filter: (salary > 1000)
```

---

## 6. Алгоритмы Selection

### 6.1 Sequential scan
Прочитать всю таблицу. Простой, но медленный. Стоит выбирать при выборке большой доли строк.

### 6.2 Index scan
Найти через индекс → достать строки из heap. Быстро при низкой селективности (мало строк).

### 6.3 Index-only scan
Если все нужные столбцы есть в индексе (covering) — heap не трогаем. Самый быстрый.

### 6.4 Bitmap scan
Index → построить битмап нужных tuple-ов → прочитать heap последовательно (без random IO). Хорошо при средней селективности.

```sql
WHERE city = 'Almaty' AND status = 'active'
→ Bitmap И двух index-сканов → объединение.
```

> [!tip] Bitmap = "много, но не очень много"
> Когда index-scan слишком много random reads, а seq-scan слишком много данных — bitmap идеален.

---

## 7. Алгоритмы Join

### 7.1 Nested-loop join

```
for each row r in R:
    for each row s in S:
        if r.x = s.x: emit (r, s)
```
- Простой.
- O(|R| × |S|) в худшем случае.
- Если на S есть индекс по join-столбцу — **index nested-loop**, очень быстро на маленькой R.

> [!tip] Когда NLJ
> R маленькая + индекс на S по join-key. Например, "взять 10 заказов и приджоинить customers".

### 7.2 Block nested-loop join
Читать R **блоками** в RAM, для каждого блока — пройти S один раз. Меньше IO.

### 7.3 Sort-merge join

```
1. Отсортировать R по join-key.
2. Отсортировать S по join-key.
3. Идти двумя курсорами параллельно, эмитить совпадения.
```
- O(|R| log |R| + |S| log |S|).
- Хорошо для больших R, S, особенно если данные уже отсортированы (индекс/CLUSTER).

### 7.4 Hash join

```
1. Build phase: хешировать R по join-key в hashtable в памяти.
2. Probe phase: для каждой s ∈ S — посмотреть в hashtable, если совпадает — эмит.
```
- O(|R| + |S|) в идеале.
- Требует RAM под hashtable (или disk-based hash join — partition).
- Самый частый алгоритм для equi-join больших таблиц.

> [!important] Сводка Join алгоритмов
> | Алгоритм | Когда выбирают |
> |---|---|
> | **Nested-loop** | одна сторона маленькая, индекс на другой |
> | **Sort-merge** | данные уже отсортированы или нужны отсортированные |
> | **Hash** | большие таблицы, equi-join, RAM есть |

---

## 8. Алгоритмы GROUP BY и DISTINCT

- **Sort-based** — сортировать → агрегировать соседние одинаковые.
- **Hash-based** — хешировать ключ → агрегировать в hashtable.

Hash быстрее, но требует RAM. Postgres выбирает тот или другой по статистике.

---

## 9. ORDER BY

- Если на столбце есть подходящий индекс → читать в порядке индекса (index scan), бесплатно.
- Иначе — сортировка (часто external merge sort, если данных больше RAM).

---

## 10. Cost estimation

Оптимизатор сравнивает планы по стоимости. Считаются:

- **IO cost** — сколько страниц прочесть.
- **CPU cost** — сколько операций.
- **Network cost** (для распределённых БД).

### 10.1 Селективность

`σ_A=v(R)` — сколько строк в среднем удовлетворяет условию?

| Условие | Эстимация селективности |
|---|---|
| `col = const` | 1 / NDV(col) |
| `col > const` | (max - const) / (max - min) |
| `col1 = col2` (equi) | 1 / max(NDV(col1), NDV(col2)) |

**NDV** = Number of Distinct Values. #abbreviation

### 10.2 Статистика

DBMS собирает:
- число строк (cardinality),
- min/max каждого столбца,
- NDV,
- гистограммы распределения (histograms).

Postgres: `ANALYZE`. Без статистики оптимизатор слепнёт.

> [!warning] Stale statistics
> Если ANALYZE не запускался, после массовых INSERT-ов оптимизатор будет принимать плохие решения. На production включай auto-analyze.

---

## 11. Cost-based vs Rule-based optimizer

| | Rule-based | Cost-based |
|---|---|---|
| Идея | фиксированные правила приоритета | минимизирует стоимость |
| Гибкость | низкая | высокая |
| Зависимость от статистики | нет | да |
| Современный стандарт | устарел | да (CBO) |

Все современные СУБД — CBO.

---

## 12. Join order

Для запроса с N таблицами нужно выбрать **порядок** JOIN-ов. Перебор всех — O(N!) → невозможно для большого N.

Стратегии:
- **Dynamic programming** (для до ~10 таблиц).
- **Greedy / heuristic** (для больших N).
- **Genetic** (Postgres GEQO).

> [!important] Selectivity-driven order
> Хорошее правило: сначала самые селективные JOIN-ы (мало строк после JOIN-а). Это уменьшает intermediate result.

---

## 13. Plan caching

Запрос → план. План каждый раз пересчитывать дорого. Решения:
- **Prepared statements** — план сохраняется.
- **Generic plans** — план без учёта конкретных значений.

> [!warning] Prepared с параметрами
> Для prepared может быть выбран generic plan, который хорош в среднем, но плох для конкретного значения. Postgres переключается между custom и generic по эвристике.

---

## 14. EXPLAIN и план запроса

```sql
EXPLAIN ANALYZE
SELECT c.name, SUM(a.balance)
FROM customers c
JOIN accounts a USING (customer_id)
WHERE c.city = 'Almaty'
GROUP BY c.name
ORDER BY SUM(a.balance) DESC;
```

Пример вывода:
```
Sort  (actual rows=100)
  Sort Key: (sum(a.balance)) DESC
  -> HashAggregate
       Group Key: c.name
       -> Hash Join
            Hash Cond: (a.customer_id = c.customer_id)
            -> Seq Scan on accounts a
            -> Hash
                 -> Index Scan using idx_customers_city on customers c
                      Index Cond: (city = 'Almaty')
```

Читать снизу вверх. Каждая строка — оператор:
- **Seq Scan** — full scan.
- **Index Scan** — через индекс.
- **Hash Join / Merge Join / Nested Loop** — JOIN алгоритмы.
- **Sort / HashAggregate** — для GROUP BY/ORDER BY.

> [!tip] EXPLAIN ANALYZE
> Запускает запрос и показывает реальное время. Без `ANALYZE` — только оценки.

---

## 15. Materialization vs Pipelining

- **Pipelining** — оператор отдаёт строки родителю по мере появления. Меньше памяти.
- **Materialization** — оператор сохраняет результат в temp area, потом отдаёт. Нужно для sort, hash join build phase.

Современные СУБД смешивают: pipeline где можно, materialize где нужно.

---

## 16. Adaptive query processing

Современные СУБД (SQL Server, Postgres extension) могут **менять план на лету**, если статистика оказалась плохой. Например, переключиться с nested-loop на hash, если строк больше ожидаемого.

---

## 17. Tuning и hints

Иногда оптимизатор ошибается. Способы помочь:
1. Обновить статистику (`ANALYZE`).
2. Создать индекс.
3. Упростить запрос (CTE, подзапросы).
4. Hints (Oracle, MySQL): принудительно сказать "используй этот индекс".
5. `pg_hint_plan` extension в Postgres.

> [!warning] Hints — последнее средство
> Hints привязывают план к запросу. Когда данные меняются, hint становится плохим. Лучше — починить статистику и индексы.

---

## 18. Распределённое выполнение (для контекста)

В распределённой БД (Citus, CockroachDB, BigQuery):
- Запрос разбивается на куски по узлам.
- Каждый узел выполняет свою часть.
- Координатор собирает результаты.

Цена — сетевой обмен. Оптимизатор учитывает и его.

---

## 19. Полный пример оптимизации

Запрос:
```sql
SELECT c.name, SUM(a.balance)
FROM customers c
JOIN accounts a ON a.customer_id = c.customer_id
WHERE c.city = 'Almaty'
GROUP BY c.name;
```

Шаги:

1. **Parse** — синтаксис ОК, имена существуют.
2. **Translate**:
   ```
   π_name,SUM(balance) (γ_name (σ_city='Almaty' (customers ⋈ accounts)))
   ```
3. **Selection pushdown**:
   ```
   π_name,SUM(balance) (γ_name (σ_city='Almaty'(customers) ⋈ accounts))
   ```
4. **Choose join algorithm**: с учётом статистики Hash Join.
5. **Choose access method**: Index scan для customers по `city`.
6. **Choose grouping**: HashAggregate.
7. Сборка: Index Scan → Hash Join → HashAggregate → result.

> [!success] Главный takeaway
> Оптимизатор переписывает запрос (logical equivalence) + выбирает физические алгоритмы (cost-based) на основе статистики.

---

## 20. Часто на экзамене

> [!danger] Exam traps
> 1. **Hash join vs sort-merge** — hash для equi-join + RAM, sort-merge если уже отсортировано.
> 2. **Nested-loop** — выгоден при маленькой R + индексе на S.
> 3. **Selection pushdown** — главное правило.
> 4. **Cost-based optimizer** требует ANALYZE/статистику.
> 5. **Index-only scan** — самый быстрый при наличии covering index.
> 6. **EXPLAIN ANALYZE** показывает реальное время.

---

## 21. Mini-quiz

1. Когда оптимизатор выберет **Seq Scan** вместо Index Scan?
2. В чём разница между **Hash Join** и **Sort-Merge Join**?
3. Почему `selection pushdown` всегда улучшает план?
4. Что измеряет `EXPLAIN` без `ANALYZE`?
5. Зачем нужна команда `ANALYZE table;`?

> [!success] Если понял эту главу
> Ты можешь читать `EXPLAIN`, понимаешь, какие алгоритмы JOIN-ов выбрал оптимизатор и почему, и можешь оптимизировать медленный запрос. Это инженерная вершина курса.
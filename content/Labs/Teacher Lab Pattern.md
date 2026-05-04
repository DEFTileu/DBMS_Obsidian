---
  protected: true
---

#labs

# Teacher Lab Pattern — как думает тичер и как он собирает lab

> [!abstract] Суть note
> Этот файл собран по `Lab1`–`Lab12`, включая `Lab11a` и `Lab11b`, плюс по карте `Learned Book topics and finished labs`.
> Цель: понять не просто темы lab, а **логику преподавателя**: что он любит проверять, как строит progression, где ставит trap и как на этой базе делать новые lab "как тичер".

## Что было проанализировано

- [[Labs/Lab1|Lab 1]] — basic IOS + ROMMON + Telnet + hidden FLAG
- [[Labs/Lab2|Lab 2]] — basic IOS configuration
- [[Labs/Lab3|Lab 3]] — Application Layer через GUI
- [[Labs/Lab4|Lab 4]] — VLSM + IPv4 static routing
- [[Labs/Lab5|Lab 5]] — IPv6 + Router-on-a-Stick + IPv6 static route + ICMP/MTU
- [[Labs/Lab6|Lab 6]] — IPv6 subnetting + ICMPv6 + NDP
- [[Labs/Lab7|Lab 7]] — Port Security + Telnet chains + FTP + troubleshooting
- [[Labs/Lab8|Lab 8]] — VLAN + Inter-VLAN Routing + L3 Switch
- [[Labs/Lab9|Lab 9]] — HSRP + OSPF
- [[Labs/Lab10|Lab 10]] — VLAN + Inter-VLAN + DHCP + Relay + RIP
- [[Labs/Lab11a|Lab 11a]] — WLC + RADIUS + WLAN + DHCP + SNMP
- [[Labs/Lab11b|Lab 11b]] — Wireless troubleshooting
- [[Labs/Lab12|Lab 12]] — Static routing + summary route + floating static route + Telnet + FTP

> [!note] Ограничение
> В локальной папке есть полноценные notes до `Lab12`. В `Learned Book topics and finished labs` ещё упоминаются `Lab 13` и `Lab 14`, но их markdown-файлов здесь нет, поэтому выводы ниже основаны на реально доступных lab notes и решениях.

## Главная мысль

Тичер почти никогда не делает lab как "одна тема = один набор команд".
Он строит lab так:

`основная тема` → `1-2 поддерживающие темы` → `один скрытый trap` → `проверка через show/ping/browser/ftp` → `процент прогресса или финальный артефакт`

То есть он проверяет не только знание команды, а умение:

- понять топологию;
- увидеть зависимость между устройствами;
- не перепутать Layer 2 и Layer 3;
- найти одно узкое место, из-за которого всё ломается;
- доказать результат через verification.

> [!important] Как думает тичер
> Для него "студент понял тему" значит не "выучил определение", а "сможет довести сеть до рабочего состояния и объяснить почему раньше не работало".

## Какие паттерны повторяются почти в каждой lab

| Паттерн | Как выглядит у тичера | Где видно |
|---|---|---|
| **Одна главная идея** | В каждой lab есть один центральный навык, вокруг которого строится всё остальное | HSRP в Lab 9, Port Security в Lab 7, WLC в Lab 11a |
| **Поддерживающие темы** | Главная тема почти всегда усиливается 1-2 соседними темами | HSRP + OSPF, DHCP + Relay + RIP, VLAN + Router-on-a-Stick |
| **Пошаговая зависимость** | Следующий шаг не работает, пока не сделан предыдущий | trunk до inter-VLAN, WAN до DNS, RADIUS до WLAN security |
| **Частичный progress** | Лаба делится на проценты: 11%, 22%, 55%, 100% | Lab 1, Lab 5, Lab 7, Lab 9, Lab 12 |
| **Один важный trap** | Есть ловушка, на которой валятся многие | `no shutdown`, wrong next-hop, wrong auth type, wrong native VLAN logic |
| **Verification как часть решения** | Команды проверки и симптомы не второстепенны, а обязательны | `show standby brief`, `show ip route`, `show port-security`, `show arp` |
| **Практическая цель** | В конце надо что-то реально получить: connectivity, file, flag, client join | FLAG, FTP file, successful ping, working WLAN |

## Какой у него общий шаблон lab

> [!tip] Формула teacher-style lab
> `Base config` → `Addressing` → `Core feature` → `Reachability` → `Troubleshooting` → `Proof`

Обычно структура lab у него такая:

1. Дать топологию или заставить студента её быстро понять.
2. Дать адресацию или заставить её вычислить.
3. Настроить базовые вещи: hostname, interfaces, VLAN, gateway, routing.
4. Добавить главную технологию lab.
5. Сломать один критичный кусок или спрятать его.
6. Заставить студента проверять сеть по слоям.
7. Довести до измеримого результата.

## Что именно тичер любит проверять

### 1. Базовая дисциплина Cisco IOS

Он очень часто проверяет базу:

- `hostname`
- `enable secret` / `enable password`
- `line console`
- `line vty`
- `banner motd`
- `service password-encryption`
- `interface vlan`
- `ip default-gateway`
- `write memory`
- `no shutdown`

Это видно уже в [[Labs/Lab1|Lab 1]] и [[Labs/Lab2|Lab 2]], и потом эта база не исчезает, а предполагается "по умолчанию понятной".

> [!warning] Вывод
> Для тичера базовая конфигурация не отдельная тема "на один раз". Это фундамент, который студент должен автоматически применять дальше в любой lab.

### 2. Layer 2 и Layer 3 как разные роли

Очень заметный паттерн: тичер любит ставить студента в точку, где надо понять:

- switch не маршрутизирует;
- VLAN режет broadcast domain;
- trunk нужен между свитчами и к роутеру;
- gateway нужен только для выхода из своей сети;
- `ip routing` нужен на L3 switch;
- `ip default-gateway` нужен обычному L2 switch.

Это центральная логика в [[Labs/Lab8|Lab 8]], [[Labs/Lab10|Lab 10]], частично в [[Labs/Lab4|Lab 4]] и [[Labs/Lab5|Lab 5]].

### 3. Адресация не ради математики, а ради конфигурации

В расчётных lab тичер не даёт математику "в вакууме".
Он всегда доводит её до сетевого смысла:

- VLSM считаетcя ради реальной адресации устройств;
- IPv6 `/48 -> /64` делается ради настройки интерфейсов;
- supernet считается ради summary route;
- /30 и /126 подаются как point-to-point logic.

То есть его логика такая:

`расчёт` → `таблица адресов` → `конфиг` → `пинг/маршрут`

Это особенно хорошо видно в [[Labs/Lab4|Lab 4]], [[Labs/Lab6|Lab 6]] и [[Labs/Lab12|Lab 12]].

### 4. Главная тема почти всегда смешана с соседней темой

Тичер почти не даёт "чистую" lab только на один feature.
Он любит связки:

| Главная тема | Что ещё рядом |
|---|---|
| VLAN | trunk, SVI, native VLAN, inter-VLAN |
| Inter-VLAN Routing | Router-on-a-Stick или L3 Switch |
| DHCP | relay agent, excluded-address, routing |
| HSRP | OSPF, default route |
| Static routing | summary route, floating static route |
| WLC | RADIUS, WPA2-Enterprise, DHCP, SNMP |
| Port Security | Telnet path, FTP, ARP, multilayer switch behavior |

> [!important] Вывод
> Новая lab "как тичер" должна иметь не одну тему, а **ядро + поддержку**.
> Пример: не просто `DHCP`, а `DHCP + Relay + VLAN`.

### 5. Troubleshooting важнее тупого набора команд

Даже когда lab формально "настройка", по факту тичер всё равно проверяет troubleshooting mindset:

- почему ping не идёт;
- почему trunk обязателен;
- почему HSRP не спасает без virtual IP на client;
- почему 802.1X не работает без RADIUS;
- почему switch не отвечает без `ip default-gateway`;
- почему backup route не виден в active routing table;
- почему GUI-сервис не работает, если проблема в DNS, а не в IP.

Отдельно troubleshooting вынесен в [[Labs/Lab7|Lab 7]] и [[Labs/Lab11b|Lab 11b]], но на самом деле он есть почти везде.

## Какие типы lab он использует

| Тип lab | Суть | Примеры |
|---|---|---|
| **Build from scratch** | Всё настраивается с нуля по шагам | Lab 1, Lab 2, Lab 8 Part 2/3, Lab 10 |
| **Calculation + apply** | Сначала считаешь, потом настраиваешь | Lab 4, Lab 6, Lab 12 |
| **Troubleshooting** | Сеть почти готова, но есть 3-5 поломок | Lab 7, Lab 11b |
| **Service validation** | Нужно проверить работу сетевых сервисов | Lab 3 |
| **Enterprise feature lab** | Один enterprise feature + поддержка | Lab 9, Lab 10, Lab 11a, Lab 12 |
| **Gamified lab** | Есть hidden target, chain, flag, remote path | Lab 1, Lab 7, частично Lab 12 |

## Какие темы тичер уже реально использовал

### Блок 1 — Foundations

| Lab | Main topic | Supporting topic |
|---|---|---|
| 1 | Basic IOS Configuration | ROMMON, Telnet, hidden device |
| 2 | Basic IOS Configuration | SVI, remote access |
| 3 | Application Layer | GUI verification, DHCP, DNS, HTTP, FTP, Email |

### Блок 2 — Addressing and Routing Fundamentals

| Lab | Main topic | Supporting topic |
|---|---|---|
| 4 | VLSM | Static routing, SVI |
| 5 | IPv6 routing | Router-on-a-Stick, static IPv6 route, MTU/ICMP |
| 6 | IPv6 subnetting | ICMPv6, NDP |

### Блок 3 — Security and Switched Networks

| Lab | Main topic | Supporting topic |
|---|---|---|
| 7 | Port Security | Telnet chains, FTP, ARP, OSPF |
| 8 | VLAN / Inter-VLAN | trunk, Router-on-a-Stick, L3 Switch |
| 9 | HSRP | OSPF, default route |
| 10 | DHCP | VLAN, relay, RIP, Router-on-a-Stick |

### Блок 4 — Wireless and Advanced Routing

| Lab | Main topic | Supporting topic |
|---|---|---|
| 11a | WLC configuration | RADIUS, 802.1X, FlexConnect, DHCP, SNMP |
| 11b | Wireless troubleshooting | Home router DHCP/DNS, WLC auth modes |
| 12 | Static routing | supernet, floating static route, Telnet, FTP |

## Самые любимые teacher-topics

Если смотреть по повторяемости, то сильнее всего повторяются:

1. **VLAN / trunk / Inter-VLAN Routing**  
   Это один из самых любимых блоков. Появляется напрямую в `Lab 5`, `Lab 8`, `Lab 10`.

2. **Static Routing / next-hop logic / default route**  
   Очень важный блок. Виден в `Lab 4`, `Lab 5`, `Lab 9`, `Lab 12`.

3. **DHCP и смежные темы**  
   DHCP как GUI-проверка, как IOS server, как relay, как WLC/internal DHCP. Появляется в `Lab 3`, `Lab 10`, `Lab 11a`, `Lab 11b`.

4. **Remote access / chained access**  
   Telnet у него не просто "команда", а механизм лабки: добраться до нужного узла через промежуточные устройства. Особенно видно в `Lab 1`, `Lab 7`, `Lab 12`.

5. **Wireless enterprise setup/troubleshooting**  
   В `Lab 11a` и `Lab 11b` тичер явно любит не только CLI, но и GUI-администрирование через WLC.

> [!tip] Короткая формула
> Если нужно угадать новую lab "в духе тичера", safest choice:
> `VLAN + routing + service + one failure point`

## Какие traps он любит

| Trap | Почему это teacher-style |
|---|---|
| Забытый `no shutdown` | Самая классическая реальная ошибка |
| Неправильный `next-hop` | Проверяет понимание пути пакета, а не память |
| Switch без `ip default-gateway` | Проверяет разницу между management plane и user traffic |
| Native VLAN / allowed VLAN logic | Проверяет понимание trunk, а не только syntax |
| Неверный тип аутентификации | PSK vs 802.1X в wireless labs |
| Не тот интерфейс | `g0/0` vs `g0/0/0`, routed port vs switchport |
| Невидимый backup route | Проверяет знание AD и active/backup behavior |
| Клиент использует real gateway вместо virtual IP | Классический HSRP concept trap |

> [!danger] Главный стиль trap
> Trap у него обычно не "невозможный". Это почти всегда **реальная админская ошибка**, которую студент должен заметить по симптомам.

## Как он делает progression внутри lab

Обычно progression выглядит так:

1. Дать стартовую рабочую зону.
2. Заставить настроить edge devices.
3. Потом backbone или routing.
4. Потом сервис.
5. Потом remote/verification.
6. Потом финальный результат.

Примеры:

- [[Labs/Lab10|Lab 10]]: switches → R1 subinterfaces → DHCP server → relay → RIP → client DHCP
- [[Labs/Lab12|Lab 12]]: IP config → Telnet path → static route → summary route → default route → backup route → FTP
- [[Labs/Lab11a|Lab 11a]]: WLC interface → RADIUS → WLAN → DHCP scope → SNMP → wireless client

## Что для тичера считается "доказательством", что lab сделана

Он любит не абстрактный финал, а конкретный observable result:

- `show` команда показывает правильное состояние;
- `ping` проходит;
- клиент получает IP по DHCP;
- `show standby brief` показывает Active/Standby;
- `show ip route` показывает статический или dynamic route;
- browser открывает страницу;
- wireless client реально подключается;
- FTP даёт скачать файл;
- FLAG реально найден.

> [!success] Teacher rule
> Если в новой lab нет понятного **proof of completion**, она будет ощущаться не как teacher-style lab, а как просто note с командами.

## Как составлять новую lab "как тичер"

### Минимальный шаблон

1. Выбери **одну центральную тему**.
2. Добавь **одну зависимую тему**, без которой главная не раскрывается.
3. Сделай **3-7 шагов** с логической зависимостью.
4. Добавь **одну типичную поломку**.
5. Привяжи всё к **топологии и адресации**.
6. Закончи **verification** и, если хочешь, `FLAG` или `file retrieval`.

### Рабочая формула для новых lab

| Уровень | Формула |
|---|---|
| Лёгкая | `Basic config + one service + verification` |
| Средняя | `VLAN + routing + one service + one trap` |
| Сильная teacher-style | `core feature + dependent feature + remote access + troubleshooting + proof` |

### Что делать обязательно

- давать таблицу адресации или правила её вычисления;
- заставлять студента проходить путь пакета головой;
- добавлять `show` команды как часть ответа;
- использовать один понятный failure point;
- делать финал измеримым.

### Что не очень похоже на этого тичера

- lab без топологии или без route logic;
- lab, где только теория и нет конфигурации;
- lab, где 20 разрозненных команд без общей истории;
- lab без verification;
- lab, где всё ломается сразу в десяти местах.

## Самый точный "teacher blueprint"

> [!important] Шаблон генерации новой lab
> 
> 1. Возьми тему из core-сетей: `VLAN`, `DHCP`, `Static Routing`, `HSRP`, `WLC`, `Port Security`
> 2. Добавь соседнюю тему: `trunk`, `relay`, `OSPF`, `summary`, `RADIUS`
> 3. Дай 1 центральный вопрос: "почему не работает?"
> 4. Раздели выполнение на progress milestones
> 5. В конце потребуй одно из:
> 
> - `show`-доказательство
> - `ping`/`browse`/`connect`
> - `FTP file`
> - `FLAG`

## Лучшие темы для новых lab в его стиле

Если делать новые lab максимально похоже на этого тичера, самые органичные варианты такие:

- `STP + trunk troubleshooting`
- `EtherChannel + VLAN trunk verification`
- `DHCP Snooping + DAI + port security`
- `HSRP + DHCP relay + failover testing`
- `Static routing troubleshooting + floating route`
- `WLAN + WPA2-Enterprise + RADIUS troubleshooting`
- `Inter-VLAN + ACL + service reachability`

> [!note] Почему именно они
> Это продолжает уже существующий стиль: один enterprise feature, одна зависимая тема, один real-world trap, одна понятная проверка.

## Короткий итог

> [!success] Если сжать стиль тичера в одну формулу
> Тичер делает не "lab на команды", а "lab на сетевое мышление":
> 
> `понять топологию` → `сделать addressing` → `включить feature` → `найти trap` → `доказать результат`
> 
> Поэтому новые lab "как тичер" должны быть не просто технически правильными, а построенными вокруг **зависимостей, симптомов и проверки результата**.

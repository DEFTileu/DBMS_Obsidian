---
  protected: true
---

#labs

# Lab 8 — VLANs & Inter-VLAN Routing

> [!abstract] Суть лабы
> Настройка VLANов на коммутаторах Cisco, Inter-VLAN routing через Router-on-a-Stick (Part 2) и L3 Switch (Part 3). Три части: создание VLANов → Router-on-a-Stick → L3 Switch routing.

## Source

https://drive.google.com/file/d/14uFymesOOSV7Y4Q9H0M53cUokdI3OrrW/view?usp=drivesdk

## Topic

- `VLANs (создание, access/trunk порты)`
- `Inter-VLAN Routing — Router-on-a-Stick`
- `Inter-VLAN Routing — L3 Switch (ip routing)`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/03 - VLANs/03 - VLANs|Book 2 Module 3 — VLANs]]
- [[Book 2. Switching, Routing, and Wireless Essentials/04 - Inter-VLAN Routing/04 - Inter-VLAN Routing|Book 2 Module 4 — Inter-VLAN Routing]]

## Цель

- Создать VLANы на коммутаторах и назначить порты (access/trunk)
- Настроить Router-on-a-Stick на роутере для Inter-VLAN routing (Part 2)
- Настроить L3 Switch с `ip routing` и SVI для Inter-VLAN routing (Part 3)
- Проверить ping между устройствами из разных VLAN

---

## Термины

**VLAN (Virtual Local Area Network)** — логическая изоляция сети на уровне коммутатора. Устройства в разных VLANах не видят друг друга без маршрутизатора. #abbreviation

**trunk port** — порт коммутатора, который передаёт трафик нескольких VLANов одновременно с 802.1Q тегами. #networkterm

**access port** — порт коммутатора, назначенный в один конкретный VLAN. Подключаются конечные устройства. #networkterm

**native VLAN** — VLAN для нетегированного трафика на trunk порту. По умолчанию VLAN 1. #networkterm

**802.1Q** — стандарт тегирования VLAN трафика на trunk портах. #abbreviation

**SVI (Switch Virtual Interface)** — виртуальный интерфейс коммутатора для управления или inter-VLAN routing на L3 свиче. #abbreviation

**broadcast domain** — область сети, в которой broadcast пакеты достигают всех устройств. Каждый VLAN — отдельный broadcast domain. #networkterm

**Router on a Stick** — техника inter-VLAN routing: один физический интерфейс роутера делится на subinterfaces, каждый для своего VLAN. #networkterm

**subinterface** — логический виртуальный интерфейс на физическом порту роутера. Обозначается как `Gig0/0.10`. #networkterm

**L3 Switch (Multilayer Switch)** — коммутатор с функциями маршрутизации (Layer 3). Может делать inter-VLAN routing без роутера. #networkterm

**ip routing** — команда включения маршрутизации на L3 свиче. #ciscoIOScommand

**default gateway** — IP адрес маршрутизатора, на который устройство отправляет трафик для других сетей. #networkterm

**encapsulation dot1Q** — команда назначения VLAN тега на subinterface роутера. #ciscoIOScommand

---

## PART 1 — Создание VLANов

> [!abstract] Суть Part 1 Создать VLANы на двух коммутаторах S1 и S2, назначить порты, настроить trunk между ними, задать IP на конечных устройствах.

**Результат:** 21 / 92 балла

### Таблица VLANов

|VLAN ID|Name|Interface|IP на S1 устройствах|IP на S2 устройствах|
|---|---|---|---|---|
|10|Full-timers|F0/10|PC1 — 192.168.10.10/24|PC2 — 192.168.10.20/24|
|15|Servers|F0/15|Ser1 — 192.168.15.10/24|Ser2 — 192.168.15.20/24|
|20|Freelancers|F0/20|L1 — 192.168.20.10/24|L2 — 192.168.20.20/24|

### IP Configuration — конечные устройства

> [!important] Настрой IP на каждом устройстве Открой устройство → Desktop → IP Configuration → Static

|Устройство|IP Address|Subnet Mask|Default Gateway|
|---|---|---|---|
|PC1 (S1)|192.168.10.10|255.255.255.0|—|
|PC2 (S2)|192.168.10.20|255.255.255.0|—|
|Ser1 (S1)|192.168.15.10|255.255.255.0|—|
|Ser2 (S2)|192.168.15.20|255.255.255.0|—|
|L1 (S1)|192.168.20.10|255.255.255.0|—|
|L2 (S2)|192.168.20.20|255.255.255.0|—|

> [!note] Gateway в Part 1 Default gateway не нужен — устройства в одном VLAN общаются напрямую через коммутатор (L2). Gateway нужен только для выхода в другие сети.

### Команды — S1 и S2 (одинаково на обоих)

```
enable
conf t

vlan 10
 name Full-timers
vlan 15
 name Servers
vlan 20
 name Freelancers
exit

interface fa0/10
 switchport mode access
 switchport access vlan 10
exit

interface fa0/15
 switchport mode access
 switchport access vlan 15
exit

interface fa0/20
 switchport mode access
 switchport access vlan 20
exit

interface gig0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,15,20
exit
```

`vlan 10` / `name Full-timers` #ciscoIOScommand Создаёт VLAN с номером 10 и даёт ему имя. Без имени VLAN работает, но имя помогает идентифицировать.

`switchport mode access` #ciscoIOScommand Переводит порт в режим access — порт принимает трафик только одного VLAN, без тегов.

`switchport access vlan 10` #ciscoIOScommand Назначает порт в VLAN 10. Трафик с этого порта будет принадлежать VLAN 10.

`switchport mode trunk` #ciscoIOScommand Переводит порт в режим trunk — порт передаёт трафик нескольких VLANов с 802.1Q тегами.

`switchport trunk allowed vlan 10,15,20` #ciscoIOScommand Разрешает проходить через trunk только указанным VLANам. Остальные VLANы блокируются.

> [!warning] Частая ошибка Если не настроить trunk между S1 и S2 — ping между PC1 и PC2 не пройдёт, даже если они в одном VLAN. Коммутатор по умолчанию ставит порт в режим access.

> [!danger] Exam trap — allowed VLANs Команда `switchport trunk allowed vlan 10,15,20` заменяет список разрешённых VLANов. Если написать `switchport trunk allowed vlan 20` отдельно — предыдущие VLANы (10, 15) будут удалены из списка!

### Почему ping PC1 → PC2 не работал? (Step 2 & 3)

> [!important] Причина По умолчанию порт Gig0/1 работает в режиме **access**, а не **trunk**. Тегированный VLAN трафик не передаётся между свичами. Решение — настроить trunk с разрешёнными VLANами.

### Почему разные VLANы не видят друг друга? (Step 4)

> [!important] Ответ для кахута Каждый VLAN — отдельный **broadcast domain**. Коммутатор работает на уровне L2 и не маршрутизирует трафик между VLANами. Для связи между VLAN 10 и VLAN 20 нужен **маршрутизатор или L3 свич**.

### Проверка

```
show vlan brief
show interfaces trunk
```

`show vlan brief` #ciscoIOScommand Показывает список всех VLANов, их статус и назначенные порты.

`show interfaces trunk` #ciscoIOScommand Показывает trunk порты, их режим, encapsulation, native VLAN и разрешённые VLANы.

---

## PART 2 — Router on a Stick

> [!abstract] Суть Part 2 Inter-VLAN routing через роутер R1. Один физический интерфейс делится на subinterfaces — по одному на каждый VLAN. Коммутатор S0 передаёт тегированный трафик через trunk к роутеру.

**Результат:** 53% / 92 балла

### Таблица VLANов

|VLAN ID|Name|Interface|Default Gateway|IP устройства|
|---|---|---|---|---|
|10|Faculty|F0/1|192.168.10.1/24|192.168.10.10/24|
|20|Students|F0/2|192.168.20.1/24|192.168.20.10/24|
|77|Servers|F0/3|192.168.77.1/24|192.168.77.10/24|
|99|MGMT|Vlan 99|192.168.99.1/24|192.168.99.2/24|

### IP Configuration — конечные устройства

> [!important] Настрой IP и Gateway на каждом устройстве Открой устройство → Desktop → IP Configuration → Static

|Устройство|IP Address|Subnet Mask|Default Gateway|
|---|---|---|---|
|PC-PT Faculty|192.168.10.10|255.255.255.0|192.168.10.1|
|Laptop-PT Student|192.168.20.10|255.255.255.0|192.168.20.1|
|Server-PT Mysdu|192.168.77.10|255.255.255.0|192.168.77.1|

> [!note] MGMT VLAN 99 VLAN 99 используется для управления коммутатором (SVI). IP 192.168.99.2 назначается на interface Vlan99 коммутатора, gateway 192.168.99.1 — это subinterface роутера.

### Команды — S0 (коммутатор)

```
enable
conf t

vlan 10
 name Faculty
vlan 20
 name Students
vlan 77
 name Servers
vlan 99
 name MGMT
exit

interface fa0/1
 switchport mode access
 switchport access vlan 10
exit

interface fa0/2
 switchport mode access
 switchport access vlan 20
exit

interface fa0/3
 switchport mode access
 switchport access vlan 77
exit

interface gig0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,77,99
exit

interface vlan 1
 shutdown
exit

interface vlan 99
 ip address 192.168.99.2 255.255.255.0
 no shutdown
exit

ip default-gateway 192.168.99.1
exit
```

`switchport trunk native vlan 99` #ciscoIOScommand Назначает VLAN 99 как native VLAN на trunk порту. Нетегированный трафик будет принадлежать VLAN 99 вместо VLAN 1.

`interface vlan 99` #ciscoIOScommand Создаёт SVI для VLAN 99 — виртуальный интерфейс для управления коммутатором.

`ip default-gateway 192.168.99.1` #ciscoIOScommand Задаёт шлюз по умолчанию для коммутатора (не для устройств). Нужен чтобы управлять свичом из других сетей.

> [!tip] Зачем нужен Native VLAN 99? По умолчанию native VLAN = 1. Оставлять VLAN 1 как native — небезопасно (VLAN hopping атаки). Смена native VLAN на 99 изолирует нетегированный трафик.

### Команды — R1 (роутер)

```
enable
conf t

interface gig0/0
 no shutdown
exit

interface gig0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
exit

interface gig0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
exit

interface gig0/0.77
 encapsulation dot1Q 77
 ip address 192.168.77.1 255.255.255.0
exit

interface gig0/0.99
 encapsulation dot1Q 99 native
 ip address 192.168.99.1 255.255.255.0
exit
```

`interface gig0/0.10` #ciscoIOScommand Создаёт subinterface .10 на физическом интерфейсе Gig0/0. Точка и номер — это логическое деление одного порта.

`encapsulation dot1Q 10` #ciscoIOScommand Говорит роутеру: трафик с тегом VLAN 10 обрабатывать на этом subinterface. Обязательно перед назначением IP.

`encapsulation dot1Q 99 native` #ciscoIOScommand Назначает subinterface для native VLAN. Слово `native` говорит роутеру принимать нетегированный трафик на этом subinterface.

> [!warning] Частая ошибка Забыть включить физический интерфейс командой `no shutdown` на `gig0/0`. Без этого все subinterfaces будут down, даже если настроены правильно.

> [!danger] Exam trap — subinterface номер Номер subinterface (`.10`) не обязан совпадать с VLAN ID — совпадение это просто best practice для читаемости. Роутер смотрит на `encapsulation dot1Q 10`, а не на `.10`.

### Проверка

```
show ip interface brief
```

`show ip interface brief` #ciscoIOScommand Кратко показывает все интерфейсы, их IP адреса и статус (up/down). Все subinterfaces должны быть up/up.

---

## PART 3 — Inter VLAN с L3 Switch

> [!abstract] Суть Part 3 Inter-VLAN routing через Multilayer Switch (3560). Вместо роутера — L3 свич с SVI интерфейсами и включённым `ip routing`. Также настраивается выход в интернет через статический маршрут.

**Результат:** 90 / 92 балла

### Таблица VLANов

|VLAN ID|Name|Interface|Default Gateway|IP устройства|
|---|---|---|---|---|
|10|HR|F0/1|10.1.1.254/24|10.1.1.1/24|
|20|Accounting|F0/2|10.1.2.254/24|10.1.2.1/24|
|30|IT|F0/3|10.1.3.254/24|10.1.3.1/24|

### IP Configuration — конечные устройства

> [!important] Настрой IP и Gateway на каждом устройстве Открой устройство → Desktop → IP Configuration → Static

|Устройство|IP Address|Subnet Mask|Default Gateway|
|---|---|---|---|
|PC-PT HR|10.1.1.1|255.255.255.0|10.1.1.254|
|Laptop-PT Accounting|10.1.2.1|255.255.255.0|10.1.2.254|
|Server-PT IT|10.1.3.1|255.255.255.0|10.1.3.254|

### Команды — Multilayer Switch (3560)

```
enable
conf t

vlan 10
 name HR
vlan 20
 name Accounting
vlan 30
 name IT
exit

interface fa0/1
 switchport mode access
 switchport access vlan 10
exit

interface fa0/2
 switchport mode access
 switchport access vlan 20
exit

interface fa0/3
 switchport mode access
 switchport access vlan 30
exit

interface vlan 10
 ip address 10.1.1.254 255.255.255.0
 no shutdown
exit

interface vlan 20
 ip address 10.1.2.254 255.255.255.0
 no shutdown
exit

interface vlan 30
 ip address 10.1.3.254 255.255.255.0
 no shutdown
exit

ip routing

interface gig0/1
 no switchport
 ip address 10.2.1.1 255.255.255.0
 no shutdown
exit

ip route 0.0.0.0 0.0.0.0 10.2.1.2
exit
```

`ip routing` #ciscoIOScommand Включает функцию маршрутизации на L3 свиче. Без этой команды свич работает только как обычный L2 коммутатор и не маршрутизирует трафик между VLANами.

`no switchport` #ciscoIOScommand Переводит порт коммутатора из режима L2 в режим L3 (routed port). После этой команды порту можно назначить IP адрес напрямую.

`ip route 0.0.0.0 0.0.0.0 10.2.1.2` #ciscoIOScommand Настраивает статический маршрут по умолчанию. Весь трафик для неизвестных сетей отправляется на 10.2.1.2 (next hop — выход в интернет).

> [!tip] L3 Switch vs Router on a Stick L3 свич быстрее Router on a Stick потому что routing происходит в hardware (ASIC чипы), а не в software. Router on a Stick создаёт bottleneck на одном физическом порту.

> [!warning] Частая ошибка Забыть команду `ip routing` на L3 свиче. SVI интерфейсы будут созданы и будут up, но трафик между VLANами не пойдёт.

> [!danger] Exam trap — no switchport Перед назначением IP на порт Gig0/1 (uplink к интернету) обязательно написать `no switchport`. Иначе получишь ошибку — коммутаторные порты не принимают IP адрес напрямую.

### Проверка

```
show ip interface brief
show vlan brief
show ip route
```

`show ip route` #ciscoIOScommand Показывает таблицу маршрутизации. Должны быть видны connected маршруты для всех VLANов и static маршрут `0.0.0.0/0`.

---

## Итоги и сравнение подходов

> [!success] Если понял лабу, умеешь:
> 
> - Создавать VLANы и назначать порты на Cisco коммутаторах
> - Настраивать trunk между коммутаторами с разрешёнными VLANами
> - Делать inter-VLAN routing через Router on a Stick (subinterfaces + dot1Q)
> - Делать inter-VLAN routing через L3 Switch (SVI + ip routing)
> - Настраивать выход в интернет через статический маршрут

|Критерий|Router on a Stick|L3 Switch|
|---|---|---|
|Оборудование|Роутер + свич|Только L3 свич|
|Скорость|Медленнее (software)|Быстрее (hardware ASIC)|
|Bottleneck|Да (один физ. порт)|Нет|
|Стоимость|Дешевле|Дороже|
|Сложность конфига|Subinterfaces + dot1Q|SVI + ip routing|
------




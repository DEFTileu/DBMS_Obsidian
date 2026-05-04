---
  protected: true
---

#labs

# Lab 9 — HSRP (First Hop Redundancy Protocol)

> [!abstract] Суть лабы
> Настроить HSRP между двумя роутерами (R1 — Active, R2 — Standby) так, чтобы клиент использовал виртуальный IP как шлюз. Если R1 падает — R2 автоматически берёт на себя трафик. Плюс OSPF для динамической маршрутизации.

## Source

Packet Tracer — задание преподавателя

## Topic

- `HSRP (Active / Standby / Virtual IP)`
- `FHRP`
- `OSPF`
- `Default Route`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/09 - FHRP Concepts/09 - FHRP Concepts|Book 2 Module 9 — FHRP Concepts]]

## Цель

- Настроить базовые IP адреса на R1, R2, R3, ISP
- Настроить HSRPv2 на R1 (Active, priority 102) и R2 (Standby, priority 101)
- Настроить OSPF для обмена маршрутами
- Проверить переключение через `show standby brief`

---

## Прогресс выполнения

R1 — 19% → R2 — 38% → R3 — 66% → R1 HSRP Active — 76% → R2 HSRP Standby — 85% → PC config — 100%

---

# HSRP Lab — First Hop Redundancy Protocol

> [!abstract] Суть темы HSRP позволяет двум роутерам работать как один виртуальный шлюз. Если активный роутер падает — резервный автоматически берёт на себя трафик. Клиенты ничего не замечают.

---

## Термины

**HSRP (Hot Standby Router Protocol)** — протокол резервирования первого хопа от Cisco. #abbreviation

**FHRP (First Hop Redundancy Protocol)** — общее название протоколов резервирования шлюза (HSRP, VRRP, GLBP). #abbreviation

**Virtual Router** — виртуальный роутер с общим IP и MAC адресом, которым пользуются все клиенты. #networkterm

**Active Router** — основной роутер, который обрабатывает весь трафик группы HSRP. #networkterm

**Standby Router** — резервный роутер, который следит за активным и готов взять управление. #networkterm

**Preemption** — право роутера вернуть себе роль Active после восстановления. #networkterm

**OSPF (Open Shortest Path First)** — протокол динамической маршрутизации, используется для обмена маршрутами между роутерами. #abbreviation

> [!important] Виртуальный IP Клиенты (PC, Server) используют **виртуальный IP** как default gateway, а не реальный IP роутера. Это ключевая идея HSRP.

---

## Топология

```
PC0 (192.168.1.10)
    |
   SW (2960)
   / \
 R1   R2          ← HSRP группа (виртуальный IP: 192.168.1.100)
   \ /
    R3
    |
   ISP (1.1.1.1)
    |
 Server0 (200.100.1.6)
```

### Таблица адресов

|Device|Interface|IP Address|Subnet Mask|
|---|---|---|---|
|R1|G0/1|172.16.13.1|255.255.255.0|
|R1|G0/0|192.168.1.1|255.255.255.0|
|R2|G0/2|172.16.23.2|255.255.255.0|
|R2|G0/0|192.168.1.2|255.255.255.0|
|R3|G0/1|172.16.13.3|255.255.255.0|
|R3|G0/2|172.16.23.3|255.255.255.0|
|R3|G0/0/0|1.1.1.2|255.255.255.252|
|ISP|G0/0/0|1.1.1.1|255.255.255.252|
|ISP|G0/0|200.100.1.1|255.255.255.248|
|Virtual Router|—|192.168.1.100|255.255.255.0|
|Server0|NIC|200.100.1.6|255.255.255.248|
|PC0|NIC|192.168.1.10|255.255.255.0|

---

## Step 1–2 — Базовые настройки и IP адреса

### R1

```cisco
enable
conf t
hostname R1
no ip domain-lookup
line console 0
 logging synchronous
 exit
interface g0/1
 ip address 172.16.13.1 255.255.255.0
 no shutdown
 exit
interface g0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit
end
write memory
```

`hostname R1` #ciscoIOScommand Задаёт имя роутера — отображается в CLI приглашении.

`no ip domain-lookup` #ciscoIOScommand Отключает DNS поиск. Без этой команды роутер зависает при опечатках, пытаясь найти хост.

`logging synchronous` #ciscoIOScommand Системные сообщения не прерывают ввод команд посередине строки.

`ip address` #ciscoIOScommand Назначает IP адрес и маску на интерфейс.

`no shutdown` #ciscoIOScommand Включает интерфейс. По умолчанию все интерфейсы роутера выключены.

> [!warning] Частая ошибка Не забывай `no shutdown` на каждом интерфейсе — иначе интерфейс останется в состоянии administratively down.

---

### R2

```cisco
enable
conf t
hostname R2
no ip domain-lookup
line console 0
 logging synchronous
 exit
interface g0/2
 ip address 172.16.23.2 255.255.255.0
 no shutdown
 exit
interface g0/0
 ip address 192.168.1.2 255.255.255.0
 no shutdown
 exit
end
write memory
```

> [!note] R1 и R2 в одной сети Оба роутера подключены к одному свитчу через G0/0 и находятся в сети 192.168.1.0/24. Это обязательное условие для работы HSRP.

---

### R3

```cisco
enable
conf t
hostname R3
no ip domain-lookup
line console 0
 logging synchronous
 exit
interface g0/1
 ip address 172.16.13.3 255.255.255.0
 no shutdown
 exit
interface g0/2
 ip address 172.16.23.3 255.255.255.0
 no shutdown
 exit
interface g0/0/0
 ip address 1.1.1.2 255.255.255.252
 no shutdown
 exit
end
write memory
```

> [!danger] Exam Trap У R3 третий интерфейс называется `g0/0/0` (не `g0/0`). Это интерфейс WAN карты. Перепутаешь — команда не применится.

---

### ISP

```cisco
enable
conf t
hostname ISP
no ip domain-lookup
line console 0
 logging synchronous
 exit
interface g0/0/0
 ip address 1.1.1.1 255.255.255.252
 no shutdown
 exit
interface g0/0
 ip address 200.100.1.1 255.255.255.248
 no shutdown
 exit
ip route 192.168.1.0 255.255.255.0 1.1.1.2
end
write memory
```

`ip route 192.168.1.0 255.255.255.0 1.1.1.2` #ciscoIOScommand Статический маршрут — ISP знает как вернуть ответ клиентам в сети 192.168.1.0/24 через R3.

---

## Step 3–7 — Конфигурация HSRP

### R1 — Active Router

```cisco
enable
conf t
interface g0/0
 standby version 2
 standby 1 ip 192.168.1.100
 standby 1 priority 102
 standby 1 preempt
 exit
end
write memory
```

`standby version 2` #ciscoIOScommand Включает HSRPv2. Версия 2 поддерживает IPv6 и большее количество групп.

`standby 1 ip 192.168.1.100` #ciscoIOScommand Задаёт виртуальный IP адрес для группы HSRP номер 1. Этот IP используют клиенты как шлюз.

`standby 1 priority 102` #ciscoIOScommand Устанавливает приоритет. Роутер с наибольшим приоритетом становится Active.

`standby 1 preempt` #ciscoIOScommand Включает preemption — роутер вернёт роль Active после восстановления если его приоритет выше.

> [!tip] Как запомнить приоритеты R1 = **102** (Active) — больше = главный R2 = **101** (Standby) — меньше = резервный Разница всего 1, но этого достаточно.

---

### R2 — Standby Router

```cisco
enable
conf t
interface g0/0
 standby version 2
 standby 1 ip 192.168.1.100
 standby 1 priority 101
 standby 1 preempt
 exit
end
write memory
```

> [!important] Одинаковый виртуальный IP На R1 и R2 виртуальный IP **одинаковый** — `192.168.1.100`. Это и есть суть HSRP — один общий адрес для двух роутеров.

---

## Step 8 — OSPF Routing

**OSPF adjacency** — состояние соседства между роутерами OSPF. Финальное состояние `FULL` означает полную синхронизацию. #networkterm

**router-id** — уникальный идентификатор роутера в OSPF, обычно задаётся вручную. #networkterm

### R1

```cisco
enable
conf t
router ospf 1
 router-id 1.1.1.1
 network 172.16.13.0 0.0.0.255 area 0
 network 192.168.1.0 0.0.0.255 area 0
 exit
end
write memory
```

`router ospf 1` #ciscoIOScommand Запускает процесс OSPF с номером 1.

`router-id 1.1.1.1` #ciscoIOScommand Задаёт уникальный ID роутера в OSPF домене.

`network 172.16.13.0 0.0.0.255 area 0` #ciscoIOScommand Включает интерфейсы в указанной сети в OSPF процесс. `0.0.0.255` — это wildcard маска (инверсия обычной маски).

**wildcard mask** — инвертированная маска подсети, используется в OSPF и ACL. `0.0.0.255` = сеть /24. #networkterm

---

### R2

```cisco
enable
conf t
router ospf 1
 router-id 2.2.2.2
 network 192.168.1.0 0.0.0.255 area 0
 network 172.16.23.0 0.0.0.255 area 0
 exit
end
write memory
```

---

### R3

```cisco
enable
conf t
ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/0
router ospf 1
 router-id 3.3.3.3
 default-information originate
 network 172.16.23.0 0.0.0.255 area 0
 network 172.16.13.0 0.0.0.255 area 0
 exit
end
write memory
```

`ip route 0.0.0.0 0.0.0.0 GigabitEthernet0/0/0` #ciscoIOScommand Default static route — весь неизвестный трафик отправляется в сторону ISP через G0/0/0.

`default-information originate` #ciscoIOScommand Распространяет default route через OSPF — R1 и R2 узнают как выйти в интернет.

> [!important] Зачем default-information originate Без этой команды R1 и R2 не будут знать маршрут в интернет даже если R3 его знает. Команда "публикует" default route в OSPF домен.

---

## Step 9 — Ответы на вопросы

### 1. Как проверить HSRP?

```cisco
show standby
show standby brief
```

`show standby brief` #ciscoIOScommand Показывает группу HSRP, виртуальный IP, роль роутера (Active/Standby) и приоритет.

---

### 2. Как настроить приоритет в HSRP?

```cisco
standby [group] priority [value]
```

Чем выше число — тем выше приоритет. Роутер с наибольшим приоритетом становится Active.

---

### 3. Если приоритеты одинаковые — кто станет Active?

Побеждает роутер с **наибольшим IP адресом** на интерфейсе HSRP.

Пример: R1=`192.168.1.1`, R2=`192.168.1.2` → победит **R2**.

> [!danger] Exam Trap Многие думают что при одинаковом приоритете побеждает роутер который первым загрузился. Нет — побеждает роутер с большим IP адресом.

---

### 4. Что такое Preemption?

**Без preempt:**

```
R1 (Active) → упал → R2 стал Active
R1 восстановился → остаётся Standby ❌
```

**С preempt:**

```
R1 (Active) → упал → R2 стал Active
R1 восстановился → забирает роль Active обратно ✅
```

> [!tip] Как запомнить Preempt = "вернуть своё место". Если R1 главный по приоритету — он всегда вернётся на своё место после восстановления.

---

### 5. Статусы HSRP и время переключения

|Статус|Описание|
|---|---|
|**Initial**|HSRP только запустился|
|**Learn**|Роутер ждёт информацию о виртуальном IP|
|**Listen**|Знает виртуальный IP, но не Active/Standby|
|**Speak**|Участвует в выборах, отправляет Hello пакеты|
|**Standby**|Резервный роутер, готов взять роль Active|
|**Active**|Основной роутер, обрабатывает весь трафик|

**Hello timer** — интервал отправки Hello пакетов = **3 секунды**. #networkterm **Hold timer** — время ожидания до признания роутера недоступным = **10 секунд**. #networkterm

> [!important] Время переключения Переключение с Active на Standby занимает **~10 секунд** (Hold timer). За это время пакеты могут теряться.

---

## Конфигурация конечных устройств

### PC0

- IP: `192.168.1.10`
- Mask: `255.255.255.0`
- Gateway: `192.168.1.100` ← виртуальный IP!

### Server0

- IP: `200.100.1.6`
- Mask: `255.255.255.248`
- Gateway: `200.100.1.1`

> [!warning] Gateway для PC0 PC0 должен использовать **виртуальный IP** `192.168.1.100` как шлюз, а не реальный IP R1 или R2. Иначе HSRP не будет работать при отказе роутера.

---

> [!success] Итог Если ты понял эту лабку — ты умеешь:
> 
> - Настраивать HSRPv2 с активным и резервным роутером
> - Задавать приоритеты и preemption
> - Настраивать OSPF для динамической маршрутизации
> - Проверять состояние HSRP командой `show standby brief`
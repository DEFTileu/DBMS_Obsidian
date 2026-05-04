---
  protected: true
---

#labs

# Lab 5 — IPv6 Routing & Inter-VLAN

> [!abstract] Суть лабы
> Настроить IPv6 адресацию на роутерах и коммутаторах, настроить Inter-VLAN routing через Router-on-a-Stick с IPv6, статическую IPv6 маршрутизацию между R1 и R2, и ICMP/MTU. Итог: 81% IPv6 + 19% ICMP = 100%.

## Source

https://drive.google.com/file/d/1IYOADzuiZ_9tc8nSznJ9xL-wqqNl9Z0/view?usp=drivesdk

## Topic

- `IPv6 unicast routing`
- `Inter-VLAN Routing (Router-on-a-Stick) с IPv6`
- `IPv6 Static Routes`
- `MTU / ICMP`

## Related Book Modules

- [[Book 1. Introduction to Networks/12 - IPv6 Addressing/12 - IPv6 Addressing|Book 1 Module 12 — IPv6 Addressing]]
- [[Book 2. Switching, Routing, and Wireless Essentials/03 - VLANs/03 - VLANs|Book 2 Module 3 — VLANs]]
- [[Book 2. Switching, Routing, and Wireless Essentials/04 - Inter-VLAN Routing/04 - Inter-VLAN Routing|Book 2 Module 4 — Inter-VLAN Routing]]

## Цель

- Настроить IPv6 GUA и link-local адреса на R1, R2, S2, S3
- Включить `ipv6 unicast-routing` на обоих роутерах
- Настроить Router-on-a-Stick на R1 для VLAN 10 и 20 через IPv6
- Добавить статические маршруты по умолчанию `::/0` на R1 и R2
- Настроить MTU и выключить нужные интерфейсы для ICMP тестов

---

---

## Термины

**IPv6 (Internet Protocol version 6)** — протокол сетевого уровня с 128-битной адресацией. Адреса записываются в шестнадцатеричном формате через двоеточие. #abbreviation

**link-local address** — IPv6 адрес для связи только в пределах одного сегмента сети. Всегда начинается с `FE80::`. Не маршрутизируется за пределы сети. #networkterm

**unicast routing** — режим маршрутизации одиночных пакетов. В IPv6 нужно явно включать командой `ipv6 unicast-routing`. #networkterm

**default route IPv6** — маршрут `::/0` — аналог `0.0.0.0/0` в IPv4. Весь трафик для неизвестных сетей отправляется по этому маршруту. #networkterm

**encapsulation dot1Q** — тегирование VLAN трафика на subinterface роутера по стандарту 802.1Q. #networkterm

**MTU (Maximum Transmission Unit)** — максимальный размер пакета в байтах который может передать интерфейс. По умолчанию 1500 байт для Ethernet. #abbreviation

**SVI (Switch Virtual Interface)** — виртуальный интерфейс коммутатора. В этой лабе используется для назначения IPv6 адреса управления. #abbreviation

**trunk port** — порт коммутатора передающий трафик нескольких VLANов с 802.1Q тегами. #networkterm

**ICMP (Internet Control Message Protocol)** — протокол диагностики сети. Используется командой `ping`. #abbreviation

---

## Система оценивания

|Задача|Points|
|---|---|
|IPv6 настройка (R1, R2, S1, S2, S3)|81%|
|ICMP настройка (MTU + shutdown)|19%|
|**Итого**|**100%**|

---

## Топология и адресация

|Устройство|Интерфейс|IPv6 Address|Link-local|
|---|---|---|---|
|R1|G0/1.10|2001:DB8:ACAD:2000::A/51|FE80::1|
|R1|G0/1.20|2001:DB8:ACAD:4000::A/51|FE80::1|
|R1|G0/0/0|2001:DB8:ACAD:A000::1/126|FE80::1|
|R2|G0/1|2001:DB8:ACAD:6000::A/51|FE80::2|
|R2|G0/2|2001:DB8:ACAD:8000::A/51|FE80::2|
|R2|G0/0/0|2001:DB8:ACAD:A000::2/126|FE80::2|
|S2|Vlan 1|2001:DB8:ACAD:6000::14/51|—|
|S3|Vlan 1|2001:DB8:ACAD:8000::14/51|—|

> [!note] Линк между R1 и R2 G0/0/0 на обоих роутерах — это point-to-point линк /126 (аналог /30 в IPv4). R1: `::1`, R2: `::2` — два адреса в подсети `A000::/126`.

---

## ЧАСТЬ 1 — IPv6 (81%)

### R1 — Router on a Stick + Static Route

> [!important] R1 делает inter-VLAN routing для VLAN 10 и VLAN 20 через subinterfaces

```
enable
configure terminal

interface g0/1.10
 encapsulation dot1Q 10
 ipv6 address 2001:DB8:ACAD:2000::A/51
 ipv6 address FE80::1 link-local
 no shutdown
exit

interface g0/1.20
 encapsulation dot1Q 20
 ipv6 address 2001:DB8:ACAD:4000::A/51
 ipv6 address FE80::1 link-local
 no shutdown
exit

interface g0/0/0
 ipv6 address 2001:DB8:ACAD:A000::1/126
 ipv6 address FE80::1 link-local
 no shutdown
exit

ipv6 unicast-routing
ipv6 route ::/0 2001:DB8:ACAD:A000::2

interface g0/1
 no shutdown
exit
```

`ipv6 address 2001:DB8:ACAD:2000::A/51` #ciscoIOScommand Назначает глобальный unicast IPv6 адрес на интерфейс. `/51` — префикс подсети.

`ipv6 address FE80::1 link-local` #ciscoIOScommand Вручную назначает link-local адрес. Используется как next-hop в статических маршрутах соседями.

`ipv6 unicast-routing` #ciscoIOScommand Включает IPv6 маршрутизацию на роутере. Без этой команды роутер не будет пересылать IPv6 пакеты между интерфейсами.

`ipv6 route ::/0 2001:DB8:ACAD:A000::2` #ciscoIOScommand Статический маршрут по умолчанию в IPv6. Весь трафик для неизвестных сетей отправляется на R2 (::2).

> [!warning] Не забудь включить физический интерфейс! `interface g0/1` → `no shutdown` — без этого subinterfaces .10 и .20 будут down, даже если настроены правильно.

---

### S1 — VLAN + Trunk (для Part ICMP)

> [!note] S1 создаёт VLANы и настраивает trunk к R1

```
enable
configure terminal

vlan 10
vlan 20

interface f0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
exit

interface f0/2
 switchport mode access
 switchport access vlan 20
 no shutdown
exit

interface g0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
exit

write memory
```

---

### R2 — IPv6 + Static Route

> [!important] R2 — роутер на другой стороне линка. Статический маршрут указывает обратно на R1.

```
enable
configure terminal

interface g0/1
 ipv6 address 2001:DB8:ACAD:6000::A/51
 ipv6 address FE80::2 link-local
 no shutdown
exit

interface g0/2
 ipv6 address 2001:DB8:ACAD:8000::A/51
 ipv6 address FE80::2 link-local
 no shutdown
exit

interface g0/0/0
 ipv6 address 2001:DB8:ACAD:A000::2/126
 ipv6 address FE80::2 link-local
 no shutdown
exit

ipv6 unicast-routing
ipv6 route ::/0 2001:DB8:ACAD:A000::1

exit
write memory
```

> [!tip] Симметрия маршрутов R1 отправляет трафик на `::2` (R2), R2 отправляет обратно на `::1` (R1). Маршруты зеркальные.

---

### S2 — Management IPv6 (2%)

```
enable
configure terminal

interface vlan 1
 ipv6 address 2001:DB8:ACAD:6000::14/51
 no shutdown
exit

write memory
```

`interface vlan 1` + `ipv6 address` #ciscoIOScommand Назначает IPv6 адрес на SVI для управления коммутатором. Адрес в той же подсети что и R2 G0/1 (`6000::/51`).

---

### S3 — Management IPv6 (2%)

```
enable
configure terminal

interface vlan 1
 ipv6 address 2001:DB8:ACAD:8000::14/51
 no shutdown
exit

write memory
```

> [!note] S2 и S3 подсети S2 (`6000::14`) в подсети R2 G0/1 (`6000::A`) S3 (`8000::14`) в подсети R2 G0/2 (`8000::A`) Оба в `/51` — одна и та же маска.

---

## ЧАСТЬ 2 — ICMP (19%)

> [!important] Что нужно сделать Настроить MTU и отключить интерфейсы для корректной работы ICMP/ping тестов.

### Router A:

```
enable
configure terminal

interface g0/0/0
 shutdown
exit

interface g0/1
 mtu 1500
exit
```

`mtu 1500` #ciscoIOScommand Устанавливает Maximum Transmission Unit = 1500 байт на интерфейсе. Стандартное значение для Ethernet. Нужно для корректной фрагментации пакетов.

### Router B:

```
interface g0/1/0
 shutdown
exit
```

> [!warning] Зачем shutdown на интерфейсах? Отключение определённых интерфейсов заставляет трафик идти через нужный путь для проверки ICMP поведения (фрагментация, TTL, MTU).

---

## Проверка

```
show ipv6 interface brief
show ipv6 route
ping ipv6 [адрес]
```

`show ipv6 interface brief` #ciscoIOScommand Кратко показывает все IPv6 интерфейсы, их адреса и статус.

`show ipv6 route` #ciscoIOScommand Показывает IPv6 таблицу маршрутизации. Должен быть виден статический маршрут `::/0`.

`ping ipv6 2001:DB8:ACAD:6000::14` #ciscoIOScommand Проверяет IPv6 связность до указанного адреса.

---

> [!success] Итог Если всё настроено правильно:
> 
> - R1 делает inter-VLAN routing для VLAN 10 и 20 через subinterfaces с IPv6
> - R1 и R2 связаны через point-to-point /126 линк
> - R2 достигает сетей VLAN 10/20 через статический маршрут на R1
> - S2 и S3 управляются по IPv6 через R2
> - ICMP тесты проходят с правильным MTU


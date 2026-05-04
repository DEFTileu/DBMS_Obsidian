---
  protected: true
---

#labs

# Lab 6 — IPv6 Subnetting & ICMP

> [!abstract] Суть лабы
> Разбить IPv6 сеть на подсети, настроить GUA и LLA адреса на устройствах, проверить связность через ICMPv6 (ping6). Понять разницу между IPv4 ARP и IPv6 NDP.

## Source

https://drive.google.com/drive/folders/1AX6hDmQ8LUUhdf-XTI0UTyfT94BM5?usp=drive_link

## Topic

- `IPv6 subnetting (/48 → /64)`
- `GUA и LLA адреса`
- `ICMPv6 / ping6`
- `NDP (Neighbor Discovery Protocol)`

## Related Book Modules

- [[Book 1. Introduction to Networks/12 - IPv6 Addressing/12 - IPv6 Addressing|Book 1 Module 12 — IPv6 Addressing]]
- [[Book 1. Introduction to Networks/13 - ICMP/13 - ICMP|Book 1 Module 13 — ICMP]]

## Цель

- Разбить IPv6 сеть (например `/48`) на подсети `/64`
- Назначить GUA и LLA адреса на интерфейсы роутера и устройств
- Включить `ipv6 unicast-routing` на роутере
- Проверить связность через `ping ipv6` и NDP таблицу

---

## Термины

**GUA (Global Unicast Address)** — глобальный IPv6 адрес, маршрутизируемый в интернете. Начинается с `2001:` или `2000::/3`. #abbreviation

**LLA (Link-Local Address)** — IPv6 адрес только для одного сегмента сети. Начинается с `FE80::/10`. Не маршрутизируется. #abbreviation

**NDP (Neighbor Discovery Protocol)** — протокол обнаружения соседей в IPv6. Заменяет ARP из IPv4. Работает через ICMPv6. #abbreviation

**ICMPv6** — протокол диагностики для IPv6. Используется ping, NDP, Router Advertisement. #abbreviation

**prefix /64** — стандартная маска подсети в IPv6. Первые 64 бита = сеть, последние 64 = хост. #networkterm

**EUI-64** — метод автоматической генерации 64-битной части IPv6 адреса из MAC адреса устройства. #networkterm

---

## IPv6 Subnetting — Шпаргалка

```
Базовая сеть:     2001:DB8:ACAD::/48
Подсети по /64:   2001:DB8:ACAD:0000::/64   (подсеть 0)
                  2001:DB8:ACAD:0001::/64   (подсеть 1)
                  2001:DB8:ACAD:0002::/64   (подсеть 2)
                  ...
```

> [!tip] Как нарезать /48 на /64
> /48 → /64 = добавляешь 16 бит под номер подсети.
> 2¹⁶ = 65536 подсетей из одной /48.
> Меняй только 4-й группой адреса (3-й октет в IPv6 нотации).

---

## Решение

### Настройка роутера

```cisco
enable
configure terminal

ipv6 unicast-routing

interface g0/0
 ipv6 address 2001:DB8:ACAD:1::1/64
 ipv6 address FE80::1 link-local
 no shutdown
 exit

interface g0/1
 ipv6 address 2001:DB8:ACAD:2::1/64
 ipv6 address FE80::1 link-local
 no shutdown
 exit

end
write memory
```

`ipv6 unicast-routing` #ciscoIOScommand Включает IPv6 маршрутизацию. Без этой команды роутер не пересылает IPv6 пакеты между интерфейсами.

`ipv6 address 2001:DB8:ACAD:1::1/64` #ciscoIOScommand Назначает GUA адрес на интерфейс. `/64` — стандартная маска подсети.

`ipv6 address FE80::1 link-local` #ciscoIOScommand Вручную назначает link-local адрес. Используется как next-hop соседями.

### Настройка конечного устройства (PC)

На PC → Desktop → IP Configuration → IPv6:
- IPv6 Address: `2001:DB8:ACAD:1::10/64`
- Default Gateway: `2001:DB8:ACAD:1::1` (или LLA роутера `FE80::1`)

### Проверка

```cisco
show ipv6 interface brief
show ipv6 neighbors
ping ipv6 2001:DB8:ACAD:1::10
```

`show ipv6 interface brief` #ciscoIOScommand Показывает все IPv6 интерфейсы, адреса и статус.

`show ipv6 neighbors` #ciscoIOScommand Показывает NDP таблицу — аналог `show arp` для IPv6.

`ping ipv6 [адрес]` #ciscoIOScommand Проверяет IPv6 связность через ICMPv6.

> [!important] NDP vs ARP
> IPv4: устройства находят друг друга через **ARP** (broadcast).
> IPv6: устройства находят друг друга через **NDP** (multicast через ICMPv6). Команда `show ipv6 neighbors` вместо `show arp`.

> [!tip] Memory Hook
> IPv6 адрес = 8 групп по 4 hex. `::` = нули. `FE80::` = всегда link-local. `2001:` = всегда глобальный.

> [!danger] Exam Trap
> LLA адрес `FE80::1` нужно указывать с именем интерфейса при использовании как next-hop:
> `ipv6 route ::/0 FE80::2 g0/0` — иначе роутер не знает через какой интерфейс его искать.

---

> [!success] Итог
> Если понял лабу — умеешь нарезать IPv6 /48 на /64 подсети, настраивать GUA и LLA адреса, включать IPv6 маршрутизацию и проверять связность через NDP/ICMPv6.

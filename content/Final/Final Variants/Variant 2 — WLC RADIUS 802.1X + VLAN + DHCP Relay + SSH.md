---
tags:
  - финал
  - вариант
  - wlc
  - radius
  - 802.1x
  - dhcp
---

# Вариант 2 — WLC с RADIUS (802.1X) + VLAN + DHCP Relay + SSH

> [!abstract] Суть варианта
> Продвинутый сценарий: RADIUS-сервер уже есть (Server-PT справа), настроить WPA2-Enterprise на WLC, DHCP Relay (если DHCP не на том же L3 коммутаторе), SSH. Этот вариант использует тот же паттерн что и Lab 11a.

---

## Ключевое отличие от Варианта 1

| | Вариант 1 | Вариант 2 |
|---|---|---|
| Wi-Fi безопасность | WPA2-PSK (один пароль) | WPA2-Enterprise (логин/пароль на RADIUS) |
| RADIUS сервер | Не нужен | Server-PT = RADIUS (172.x.x.x) |
| DHCP | Локально на 3650 | Relay к серверу или Internal WLC |
| Сложность | Средняя | Высокая |

---

## Таблица адресации

| Устройство | Интерфейс | IP адрес | Маска | Gateway |
|---|---|---|---|---|
| 3650-LEFT | VLAN 10 SVI | 192.168.10.1 | 255.255.255.0 | — |
| 3650-LEFT | VLAN 20 SVI | 192.168.20.1 | 255.255.255.0 | — |
| 3650-LEFT | VLAN 99 SVI | 192.168.99.1 | 255.255.255.0 | — |
| Server-PT RIGHT | NIC | 172.31.1.100 | 255.255.255.0 | 172.31.1.1 |
| WLC-3504 | Management | 192.168.99.10 | 255.255.255.0 | 192.168.99.1 |
| Laptop (wireless) | Wi-Fi | DHCP | — | DHCP |

> [!note] Почему Server-PT в сети 172.31.x.x?
> Часто в топологии RADIUS/DHCP сервер находится в отдельной "management" сети. WLC должен до него дотянуться — нужен маршрут или они в одной сети.

---

## Возможные пароли

| Что | Значение |
|---|---|
| Enable secret | `cisco` |
| SSH username | `admin` |
| SSH password | `Cisco123` |
| WLC login | `admin` / `Cisco123` |
| RADIUS Shared Secret | `Cisco123` |
| WLAN User login | `user1` |
| WLAN User password | `User1Pass` |

---

## Часть 1 — Базовая конфигурация (то же что Вариант 1)

```cisco
en
conf t
hostname SW-ACCESS
enable secret cisco
line console 0
 password cisco
 login
line vty 0 15
 password cisco
 login
service password-encryption
no ip domain-lookup
end
```

---

## Часть 2 — VLAN и Trunk (то же что Вариант 1)

```cisco
conf t
vlan 10
 name Wired-Clients
vlan 20
 name Wireless-Clients
vlan 99
 name Management
end
```

Trunk между 3650 ↔ 3560 ↔ 2960:

```cisco
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,99
 no shutdown
```

---

## Часть 3 — Inter-VLAN Routing на 3650

```cisco
conf t
ip routing

interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 no shutdown

interface Vlan99
 ip address 192.168.99.1 255.255.255.0
 no shutdown
end
```

---

## Часть 4 — DHCP Relay (если DHCP сервер не на 3650)

Если DHCP сервер = Server-PT (например `192.168.10.100`), а клиенты в VLAN 20 — нужен relay:

```cisco
conf t
interface Vlan20
 ip helper-address 192.168.10.100
end
```

> [!important] Когда нужен ip helper-address?
> Если DHCP сервер в **другой подсети** от клиентов. DHCP Discover — broadcast, роутер его не пропустит без relay. `ip helper-address` превращает broadcast в unicast к серверу.

> [!tip] Если DHCP прямо на 3650 — relay не нужен
> Просто настрой пул как в Варианте 1. Relay нужен только если сервер в другой сети.

---

## Часть 5 — SSH на 3650

```cisco
conf t
hostname SW-CORE
ip domain-name sdu.edu.kz
crypto key generate rsa
! → 1024
ip ssh version 2
username admin secret Cisco123
line vty 0 15
 transport input ssh
 login local
end
```

---

## Часть 6 — WLC (GUI) с RADIUS 802.1X

### Шаг 1 — Войти в WLC

```
https://192.168.99.10
admin / Cisco123
```

### Шаг 2 — Добавить RADIUS сервер

**Путь:** `Security → AAA → RADIUS → Authentication → New`

| Поле | Значение |
|---|---|
| Server IP Address | `172.31.1.100` (IP сервера) |
| Shared Secret | `Cisco123` |
| Port | `1812` (default) |

→ **Apply**

> [!warning] Shared Secret должен совпадать
> Этот же ключ должен быть настроен на RADIUS сервере. Иначе 802.1X не работает — WLC и сервер не доверяют друг другу.

### Шаг 3 — Создать VLAN интерфейс на WLC

**Путь:** `Controller → Interfaces → New`

| Поле | Значение |
|---|---|
| Interface Name | `wireless-vlan20` |
| VLAN ID | `20` |
| IP Address | `192.168.20.254` |
| Netmask | `255.255.255.0` |
| Gateway | `192.168.20.1` |
| Primary DHCP | `192.168.20.1` |

→ **Apply → Save Configuration**

### Шаг 4 — Создать WLAN

**Путь:** `WLANs → Create New → Go`

| Поле | Значение |
|---|---|
| Profile Name | `SDU-Enterprise` |
| SSID | `SDU-WiFi` |
| ID | `1` |

→ **Apply**

### Шаг 5 — Настроить WLAN Security (802.1X)

**Вкладка General:**
- ✅ Status: Enabled
- Interface: `wireless-vlan20`

**Вкладка Security → Layer 2:**
- Security: `WPA+WPA2`
- ✅ WPA2 Policy
- Auth Key Mgmt: **802.1X** (НЕ PSK!)

**Вкладка Security → AAA Servers:**
- Server 1: `172.31.1.100` (должен появиться из Шага 2)

→ **Apply → Save Configuration**

> [!danger] Trap — порядок шагов WLC
> RADIUS сервер ДОЛЖЕН быть добавлен в Security → RADIUS **до того**, как ты его выберешь в AAA Servers WLAN. Иначе он не появится в выпадающем списке!

### Шаг 6 (опционально) — FlexConnect

**Вкладка Advanced:**
- ✅ FlexConnect Local Switching
- ✅ FlexConnect Local Auth

→ **Apply**

---

## Часть 7 — Подключить Wireless ноутбуки (802.1X)

**На каждом Laptop-PT:**

`Desktop → PC Wireless → Profiles → New`

1. Profile Name: `SDU`
2. Выбери сеть: `SDU-WiFi`
3. IP Configuration: DHCP
4. Security: **WPA2-Enterprise**
5. Username: `user1`
6. Password: `User1Pass`
7. **Save → Connect to Network**

> [!danger] Регистр важен!
> `user1` ≠ `User1`. Вводи точно как задано.

---

## Проверка

```cisco
! На 3650:
show ip route
show ip dhcp binding
show vlan brief
show interfaces trunk

! SSH проверка с другого устройства:
ssh -l admin 192.168.99.1

! На WLC (GUI):
Monitor → Clients → должны отображаться подключённые клиенты
```

---

## Итог

> [!success] Если понял — умеешь:
> - Настраивать WPA2-Enterprise через WLC + RADIUS
> - Добавлять RADIUS сервер в WLC и связывать с WLAN
> - Настраивать DHCP Relay (ip helper-address)
> - Понимать разницу PSK vs 802.1X
> - Подключать клиентов с индивидуальным логином

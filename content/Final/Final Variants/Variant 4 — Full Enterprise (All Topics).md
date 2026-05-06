---
tags:
  - финал
  - вариант
  - enterprise
  - полный
---

# Вариант 4 — Full Enterprise (Все темы вместе)

> [!abstract] Суть варианта
> Самый сложный вариант — всё сразу: VLAN + Inter-VLAN + DHCP + DHCP Relay + SSH + Telnet + WLC (802.1X или PSK) + Static Route. Используй этот вариант для полной подготовки. Разбит по частям с процентами progress.

---

## Топология

```
[Internet]
    |
[Server-PT LEFT]──[3650-24PS LEFT]══trunk══[3650-24PS RIGHT]──[Server-PT RIGHT]
                       ║                        ║
                  [3560-24PS]──────────────[3560-24PS]
                       ║                        ║──────[WLC-3504]
                  [2960-24TT]              [2960-24TT]      |
                  /    |    \             /    |    \    [3702i AP]
              Laptop  Laptop Laptop  Laptop Laptop Laptop  ↑
              (wired)                          (3 wireless, без кабелей)
```

---

## Таблица адресации

| Устройство | Interface | IP | Маска | Gateway |
|---|---|---|---|---|
| 3650-LEFT | VLAN 10 SVI | 192.168.10.1 | /24 | — |
| 3650-LEFT | VLAN 20 SVI | 192.168.20.1 | /24 | — |
| 3650-LEFT | VLAN 30 SVI | 192.168.30.1 | /24 | — |
| 3650-LEFT | VLAN 99 SVI | 192.168.99.1 | /24 | — |
| 3650-RIGHT | VLAN 99 SVI | 192.168.99.2 | /24 | — |
| 2960-LEFT | VLAN 99 (mgmt) | 192.168.99.10 | /24 | 192.168.99.1 |
| 2960-RIGHT | VLAN 99 (mgmt) | 192.168.99.11 | /24 | 192.168.99.1 |
| WLC-3504 | Management | 192.168.99.254 | /24 | 192.168.99.1 |
| Server-PT LEFT | NIC | 192.168.30.10 | /24 | 192.168.30.1 |
| Server-PT RIGHT (RADIUS) | NIC | 172.31.1.254 | /24 | 172.31.1.1 |

---

## Пароли — финальная шпаргалка

| Роль | Username | Password |
|---|---|---|
| Enable | — | `cisco` |
| Console | — | `cisco` |
| VTY Telnet | — | `cisco` |
| SSH | `admin` | `cisco` или `Cisco123` |
| WLC GUI | `admin` | `Cisco123` |
| RADIUS Shared Key | — | `Cisco123` |
| WLAN PSK | — | `Cisco123` |
| WLAN 802.1X user | `user1` | `User1Pass` |

---

## Часть 1 — Базовая конфигурация на ВСЕХ устройствах (11%)

На каждом коммутаторе:

```cisco
en
conf t
hostname [SW-LEFT / SW-RIGHT / SW-ACCESS1 / SW-ACCESS2]
enable secret cisco
no ip domain-lookup
service password-encryption
banner motd #WARNING: Authorized access only!#

line console 0
 password cisco
 login
 logging synchronous

line vty 0 15
 password cisco
 login
 transport input telnet ssh
 logging synchronous
end
write memory
```

**Результат: 11%** ✅

---

## Часть 2 — VLAN и назначение портов (22%)

### На всех коммутаторах:

```cisco
conf t
vlan 10
 name Wired-Data
vlan 20
 name Wireless
vlan 30
 name Servers
vlan 99
 name Management
vlan 999
 name Native-Unused
end
```

### На 2960 (access порты):

```cisco
! Порты к проводным ноутбукам
interface range Fa0/1 - 10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown

! Uplink к 3560
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99,999
 no shutdown

! Management SVI
interface Vlan99
 ip address 192.168.99.10 255.255.255.0
 no shutdown

ip default-gateway 192.168.99.1
end
```

### На 3560 (uplink к 3650, downlink к 2960):

```cisco
! К 2960 (уже trunk)
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
 no shutdown

! К 3650 (тоже trunk)
interface GigabitEthernet0/2
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,99
 no shutdown
end
```

**Результат: 22%** ✅

---

## Часть 3 — Inter-VLAN Routing на 3650-LEFT (40%)

```cisco
conf t
ip routing

interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 no shutdown

interface Vlan20
 ip address 192.168.20.1 255.255.255.0
 no shutdown

interface Vlan30
 ip address 192.168.30.1 255.255.255.0
 no shutdown

interface Vlan99
 ip address 192.168.99.1 255.255.255.0
 no shutdown
end
```

### Проверка:

```cisco
show ip route
! Должен видеть: C 192.168.10.0/24, C 192.168.20.0/24, C 192.168.30.0/24
```

**Результат: 40%** ✅

---

## Часть 4 — DHCP сервер на 3650-LEFT (55%)

```cisco
conf t
! Исключённые адреса (статика)
ip dhcp excluded-address 192.168.10.1 192.168.10.20
ip dhcp excluded-address 192.168.20.1 192.168.20.20
ip dhcp excluded-address 192.168.30.1 192.168.30.20

! Пул для VLAN 10
ip dhcp pool WIRED
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 8.8.8.8
 lease 7

! Пул для VLAN 20 (wireless)
ip dhcp pool WIRELESS
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8
 lease 1
end
```

> [!important] Если DHCP сервер на отдельном Server-PT
> Тогда на интерфейсах VLAN нужен relay:
> ```cisco
> interface Vlan10
>  ip helper-address 192.168.30.10
> interface Vlan20
>  ip helper-address 192.168.30.10
> ```

**Результат: 55%** ✅

---

## Часть 5 — SSH на 3650-LEFT (65%)

```cisco
conf t
! hostname уже задан
ip domain-name sdu.edu.kz
crypto key generate rsa modulus 1024
ip ssh version 2
username admin privilege 15 secret Cisco123
line vty 0 15
 transport input ssh
 login local
end
write memory
```

### Проверка с Admin PC:

```
> ssh -l admin 192.168.99.1
Password: Cisco123
SW-CORE#
```

**Результат: 65%** ✅

---

## Часть 6 — WLC (GUI) — WLAN настройка (85%)

### 6.1 — Войти

```
https://192.168.99.254
admin / Cisco123
```

### 6.2 — Создать VLAN Interface

**Controller → Interfaces → New**

| Поле | Значение |
|---|---|
| Interface Name | `wlan-20` |
| VLAN ID | `20` |
| IP Address | `192.168.20.254` |
| Netmask | `255.255.255.0` |
| Gateway | `192.168.20.1` |
| Primary DHCP Server | `192.168.20.1` |

→ Apply → Save

### 6.3 — (Если RADIUS) Добавить сервер

**Security → AAA → RADIUS → Authentication → New**

| Поле | Значение |
|---|---|
| Server IP | `172.31.1.254` |
| Shared Secret | `Cisco123` |

→ Apply

### 6.4 — Создать WLAN

**WLANs → Create New → Go**

| Поле | Значение |
|---|---|
| Profile Name | `Enterprise-WLAN` |
| SSID | `SDU-Net` |
| WLAN ID | `1` |

→ Apply

**General вкладка:**
- ✅ Enabled
- Interface: `wlan-20`

**Security → Layer 2:**

**Вариант A (PSK):**
- WPA+WPA2 → ✅ WPA2 → PSK → ASCII → `Cisco123`

**Вариант B (802.1X):**
- WPA+WPA2 → ✅ WPA2 → 802.1X
- **AAA Servers вкладка** → Server 1: `172.31.1.254`

→ Apply → Save Configuration

**Результат: 85%** ✅

---

## Часть 7 — Подключить 3 wireless ноутбука (100%)

**Каждый Laptop-PT (wireless):**

`Desktop → PC Wireless → Connect`

**Для PSK:**
- Выбери `SDU-Net` → Enter key: `Cisco123`

**Для 802.1X:**
- Выбери `SDU-Net` → Profiles → New
- Security: WPA2-Enterprise
- Username: `user1`, Password: `User1Pass`

**Проверить:**
- Laptop получил IP из диапазона 192.168.20.21+
- Ping: `ping 192.168.10.1` (шлюз другого VLAN) → должен работать

**Результат: 100%** 🎯

---

## Мегашпаргалка — критические команды по порядку

```cisco
! === БАЗОВАЯ КОНФИГ ===
hostname NAME
enable secret cisco
no ip domain-lookup
service password-encryption
line vty 0 15 → password cisco → login → transport input telnet ssh

! === VLAN ===
vlan 10 → name ...
switchport mode access → switchport access vlan 10
switchport mode trunk → switchport trunk native vlan 999

! === INTER-VLAN L3 ===
ip routing                          ! ОБЯЗАТЕЛЬНО на 3650!
interface Vlan10 → ip address ... → no shutdown

! === DHCP ===
ip dhcp excluded-address 192.168.x.1 192.168.x.10
ip dhcp pool NAME → network ... → default-router ... → dns-server 8.8.8.8

! === DHCP RELAY (если сервер в другой сети) ===
interface VlanXX → ip helper-address [IP DHCP сервера]

! === SSH ===
hostname NAME          ! не default!
ip domain-name x.com   ! обязательно!
crypto key generate rsa modulus 1024
ip ssh version 2
username admin secret cisco
line vty 0 15 → transport input ssh → login local

! === L2 SWITCH MANAGEMENT ===
interface Vlan99 → ip address 192.168.99.x /24 → no shutdown
ip default-gateway 192.168.99.1   ! только на L2!

! === WLC (GUI, запомни путь) ===
Controller → Interfaces → New → [VLAN Interface]
Security → AAA → RADIUS → New → [RADIUS server IP + Shared Secret]
WLANs → Create New → [SSID + Profile] → Security [PSK или 802.1X]
```

---

## Топ-5 trap этого финала

| # | Trap | Как не попасться |
|---|---|---|
| 1 | Забыл `ip routing` на 3650 | Всегда первым делом после `ip routing` — SVI |
| 2 | Забыл `ip domain-name` перед `crypto key` | Порядок: hostname → domain → crypto key |
| 3 | RADIUS сервер не выбирается в WLC WLAN | Сначала добавить в Security → RADIUS, потом в WLAN |
| 4 | Wireless клиент не получает IP | Проверить Primary DHCP на WLC Interface; проверить DHCP пул |
| 5 | Нет trunk между 3650 и 3560 | `show interfaces trunk` — порты должны быть в списке |

---

> [!success] Итог варианта 4
> Это полная Enterprise конфигурация. Если можешь пройти всё от начала до конца без подсказок — финал ты сдашь.

---
tags:
  - финал
  - вариант
  - wlc
  - vlan
  - dhcp
  - ssh
---

# Вариант 1 — VLAN + Inter-VLAN Routing + DHCP + WLC (PSK) + SSH

> [!abstract] Суть варианта
> Самый вероятный сценарий финала. Настроить VLAN на коммутаторах, Inter-VLAN Routing на L3 коммутаторе, DHCP сервер, WLC с WLAN по WPA2-Personal (PSK), SSH доступ. Три ноутбука подключаются по Wi-Fi без кабеля.

---

## Топология (по img.png)

```
[Server-PT]─────[3650-24PS LEFT]══════════[3650-24PS RIGHT]─────[Server-PT]
                       ║   ══ trunk ══          ║
                  [3560-24PS]──────────────[3560-24PS]
                       ║                        ║────[WLC-3504]────[3702i AP]
                  [2960-24TT]              [2960-24TT]             (Laptop-PT × 3 wireless)
                  [Laptop-PT]              [Laptop-PT]
```

---

## Таблица адресации

| Устройство | Интерфейс | IP адрес | Маска | Gateway |
|---|---|---|---|---|
| 3650-LEFT | VLAN 10 SVI | 192.168.10.1 | 255.255.255.0 | — |
| 3650-LEFT | VLAN 20 SVI | 192.168.20.1 | 255.255.255.0 | — |
| 3650-LEFT | VLAN 99 SVI | 192.168.99.1 | 255.255.255.0 | — |
| WLC-3504 | Management | 192.168.99.254 | 255.255.255.0 | 192.168.99.1 |
| Server-PT LEFT | NIC | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 |
| Laptop (wired) | NIC | DHCP | — | DHCP |
| Laptop (wireless) | Wi-Fi | DHCP | — | DHCP |

---

## Возможные пароли (запомни наизусть)

| Что | Значение |
|---|---|
| Enable secret | `cisco` или `class` |
| VTY password (Telnet) | `cisco` |
| SSH username | `admin` |
| SSH password | `cisco` или `Cisco123` |
| WLC login | `admin` / `Cisco123` |
| WLAN PSK (Wi-Fi пароль) | `Cisco123` или `cisco123` |
| Console password | `cisco` |

---

## Часть 1 — Базовая конфигурация коммутаторов

### На каждом коммутаторе (2960, 3560, 3650):

```cisco
en
conf t
hostname SW1
enable secret cisco
line console 0
 password cisco
 login
line vty 0 15
 password cisco
 login
 transport input telnet ssh
service password-encryption
banner motd #Unauthorized access prohibited#
no ip domain-lookup
end
write memory
```

> [!warning] Trap #1
> `no ip domain-lookup` — без этой команды коммутатор будет зависать при опечатках, пытаясь резолвить DNS. Часто забывают!

---

## Часть 2 — Создание VLAN

### На всех коммутаторах (2960, 3560, 3650):

```cisco
conf t
vlan 10
 name Students
vlan 20
 name Wireless
vlan 99
 name Management
vlan 999
 name Native
end
```

> [!tip] Зачем VLAN 999?
> Native VLAN лучше вынести в отдельный неиспользуемый VLAN — это best practice безопасности. Меняется командой `switchport trunk native vlan 999`.

---

## Часть 3 — Настройка trunk и access портов

### На 3650-LEFT (uplink к 3560):

```cisco
conf t
interface GigabitEthernet1/0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99,999
 no shutdown
end
```

### На 2960 (порты к ноутбукам → access):

```cisco
conf t
interface range FastEthernet0/1 - 5
 switchport mode access
 switchport access vlan 10
 no shutdown
end
```

### На 2960 (порт к WLC → access VLAN 99 или trunk):

```cisco
conf t
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 99
 no shutdown
end
```

> [!important] WLC порт
> WLC может требовать trunk если он обслуживает несколько WLAN на разных VLAN. В простом варианте — access VLAN 99 (Management).

---

## Часть 4 — Inter-VLAN Routing на L3 коммутаторе (3650)

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

> [!danger] Trap #2 — `ip routing`
> На L3 коммутаторе (3650/3560) ОБЯЗАТЕЛЬНО нужна команда `ip routing`. Без неё коммутатор не маршрутизирует между VLAN, даже если SVI настроены.

---

## Часть 5 — DHCP на 3650

```cisco
conf t

! Исключить статические адреса из пула
ip dhcp excluded-address 192.168.10.1 192.168.10.10
ip dhcp excluded-address 192.168.20.1 192.168.20.10

! Пул для VLAN 10 (Students)
ip dhcp pool VLAN10_POOL
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 8.8.8.8

! Пул для VLAN 20 (Wireless)
ip dhcp pool VLAN20_POOL
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8
end
```

> [!note] Проверка DHCP
> ```cisco
> show ip dhcp binding        ! кому выданы адреса
> show ip dhcp pool           ! состояние пулов
> show ip dhcp conflict       ! конфликты
> ```

---

## Часть 6 — SSH на 3650

```cisco
conf t
hostname SW-CORE
ip domain-name cisco.com
crypto key generate rsa
! → выбери 1024 бит
ip ssh version 2
username admin secret cisco
line vty 0 15
 transport input ssh
 login local
end
```

> [!danger] Trap #3 — порядок SSH
> `ip domain-name` ОБЯЗАТЕЛЬНО до `crypto key generate rsa`. Без домена ключ не генерируется! Hostname должен быть НЕ default (не Switch/Router).

---

## Часть 7 — WLC (GUI через браузер)

### Шаг 1 — Войти в WLC

```
Браузер → https://192.168.99.254
Login: admin
Password: Cisco123
```

### Шаг 2 — Создать WLAN Interface (для Wireless VLAN)

**Путь:** `Controller → Interfaces → New`

| Поле | Значение |
|---|---|
| Interface Name | `wireless-vlan` |
| VLAN ID | `20` |
| IP Address | `192.168.20.254` |
| Netmask | `255.255.255.0` |
| Gateway | `192.168.20.1` |
| Primary DHCP | `192.168.20.1` |

→ **Apply → Save Configuration**

### Шаг 3 — Создать WLAN

**Путь:** `WLANs → Create New → Go`

| Поле | Значение |
|---|---|
| Profile Name | `Final-WLAN` |
| SSID | `Final-WiFi` |
| ID | `1` |

→ **Apply**

### Шаг 4 — Настроить безопасность WLAN (PSK)

**Вкладка General:**
- ✅ Status: **Enabled**
- Interface: `wireless-vlan`

**Вкладка Security → Layer 2:**
- Security: `WPA+WPA2`
- ✅ WPA2 Policy
- Auth Key Mgmt: **PSK**
- PSK Format: **ASCII**
- PSK: `Cisco123`

→ **Apply → Save Configuration**

> [!tip] PSK vs 802.1X
> PSK = один пароль для всех. 802.1X = индивидуальный логин через RADIUS. На финале скорее всего PSK (проще, нет RADIUS сервера в задании).

---

## Часть 8 — Подключить Wireless ноутбуки

**На каждом Laptop-PT (беспроводном):**

`Desktop → PC Wireless → Connect`

1. Выбери сеть `Final-WiFi`
2. Введи PSK: `Cisco123`
3. Убедись что IP получен по DHCP

---

## Проверка — команды

```cisco
! Проверить VLAN
SW# show vlan brief

! Проверить trunk
SW# show interfaces trunk

! Проверить маршрутизацию
SW-CORE# show ip route

! Проверить DHCP
SW-CORE# show ip dhcp binding

! Проверить SSH
SW-CORE# show ip ssh

! Пинг между VLAN
SW-CORE# ping 192.168.20.1 source vlan 10
```

---

## Итог — что ты умеешь после этого варианта

> [!success] Если понял — умеешь:
> - Создавать VLAN и назначать порты
> - Настраивать trunk между коммутаторами
> - Включать IP routing на L3 коммутаторе
> - Настраивать DHCP для нескольких VLAN
> - Настраивать SSH пошагово
> - Создавать WLAN на WLC с WPA2-PSK
> - Подключать беспроводных клиентов

---
tags:
  - финал
  - вариант
  - telnet
  - ssh
  - wlc
---

# Вариант 3 — Telnet Chain + SSH + VLAN + WLC (PSK)

> [!abstract] Суть варианта
> Тичер любит Telnet chain (доступ через цепочку устройств — Lab 1, Lab 7, Lab 12). Здесь: подключиться по Telnet к коммутаторам, настроить SSH, VLAN, и WLC. Нет консольного кабеля — весь доступ только через сеть.

---

## Ключевой момент — почему нет консольного кабеля

> [!important] Сценарий: консольный кабель недоступен
> По условию финала — нет консольного кабеля к некоторым устройствам. Единственный способ попасть — через **Telnet** (или SSH если уже настроен). Это значит:
> 1. Базовая конфигурация уже частично есть на устройствах (VTY настроен)
> 2. Ты подключаешься с одного устройства к другому через сеть
> 3. Ошибиться в IP/маске нельзя — потеряешь доступ

---

## Таблица адресации

| Устройство | Interface/VLAN | IP адрес | Маска | VTY Password |
|---|---|---|---|---|
| 3650-LEFT | VLAN 99 | 192.168.99.2 | 255.255.255.0 | cisco |
| 3650-RIGHT | VLAN 99 | 192.168.99.3 | 255.255.255.0 | cisco |
| 3560-LEFT | VLAN 99 | 192.168.99.4 | 255.255.255.0 | cisco |
| 3560-RIGHT | VLAN 99 | 192.168.99.5 | 255.255.255.0 | cisco |
| 2960-LEFT | VLAN 99 | 192.168.99.6 | 255.255.255.0 | cisco |
| 2960-RIGHT | VLAN 99 | 192.168.99.7 | 255.255.255.0 | cisco |
| WLC-3504 | Management | 192.168.99.254 | 255.255.255.0 | — |
| Admin PC | NIC | 192.168.99.50 | 255.255.255.0 | 192.168.99.1 |

> [!note] ip default-gateway на L2 коммутаторах
> 2960 — это L2 коммутатор. Он сам не маршрутизирует. Для управления через сеть нужен:
> ```cisco
> ip default-gateway 192.168.99.1
> ```

---

## Возможные пароли

| Что | Значение |
|---|---|
| Enable secret | `cisco` или `class` |
| VTY Telnet password | `cisco` |
| SSH username | `admin` |
| SSH password | `cisco` |
| Console password | `cisco` |
| WLC login | `admin` / `Cisco123` |
| WLAN PSK | `Cisco123` |

---

## Часть 1 — Telnet chain к коммутаторам

Если устройства уже частично настроены (VTY есть), подключаешься так:

```
Admin PC → Telnet 192.168.99.2  (3650-LEFT)
         → Telnet 192.168.99.3  (3650-RIGHT)
         → Telnet 192.168.99.6  (2960-LEFT)
```

**Команда с Admin PC:**

```
> telnet 192.168.99.2
Password: cisco
SW-CORE> enable
Password: cisco
SW-CORE#
```

> [!tip] Как вернуться назад
> Ctrl+Shift+6 затем X — вернуться к предыдущему устройству в цепочке.

---

## Часть 2 — Настройка SSH на всех коммутаторах

После подключения через Telnet — настраиваем SSH:

```cisco
conf t
hostname SW-CORE
ip domain-name final.lab
crypto key generate rsa
! → 1024 bits
ip ssh version 2
username admin secret cisco
line vty 0 15
 transport input ssh telnet
 login local
end
write memory
```

> [!danger] Trap — после настройки SSH
> Если поставить `transport input ssh` (только SSH) — текущая Telnet сессия ОБРЫВАЕТСЯ! Используй `transport input ssh telnet` пока не убедишься что SSH работает.

### Проверка SSH:

```cisco
SW# show ip ssh
! Должно показать: SSH Enabled - version 2.0

! Подключиться по SSH с Admin PC:
> ssh -l admin 192.168.99.2
Password: cisco
```

---

## Часть 3 — VLAN и Inter-VLAN Routing

### Создать VLAN на всех свитчах:

```cisco
conf t
vlan 10
 name Data
vlan 20
 name Voice
vlan 99
 name Management
vlan 999
 name Native-Unused
end
```

### Trunk между 3650 ↔ 3560 ↔ 2960:

```cisco
interface GigabitEthernet1/0/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99
 no shutdown
```

### Access порты на 2960:

```cisco
interface range FastEthernet0/1 - 10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown
```

### SVI и IP routing на 3650:

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

### ip default-gateway на 2960 (L2):

```cisco
conf t
ip default-gateway 192.168.99.1
end
```

---

## Часть 4 — DHCP на 3650

```cisco
conf t
ip dhcp excluded-address 192.168.10.1 192.168.10.20
ip dhcp excluded-address 192.168.20.1 192.168.20.20

ip dhcp pool DATA
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 8.8.8.8

ip dhcp pool WIRELESS
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8
end
```

---

## Часть 5 — WLC (GUI) с WPA2-PSK

### Войти в WLC:

```
https://192.168.99.254
admin / Cisco123
```

### Создать WLAN Interface:

**Controller → Interfaces → New**

| Поле | Значение |
|---|---|
| Interface Name | `wireless` |
| VLAN ID | `20` |
| IP Address | `192.168.20.254` |
| Netmask | `255.255.255.0` |
| Gateway | `192.168.20.1` |
| Primary DHCP | `192.168.20.1` |

→ Apply → Save

### Создать WLAN:

**WLANs → Create New → Go**

| Поле | Значение |
|---|---|
| Profile Name | `Final-Exam` |
| SSID | `Final-Net` |
| ID | `1` |

→ Apply

### Security — WPA2 PSK:

**Security → Layer 2:**
- WPA+WPA2
- ✅ WPA2 Policy
- Auth Key Mgmt: **PSK**
- PSK (ASCII): `Cisco123`

→ Apply → Save Configuration

---

## Часть 6 — Подключить 3 wireless ноутбука

На каждом Laptop-PT (без кабеля):

`Desktop → PC Wireless → Connect`

1. Сеть: `Final-Net`
2. Password: `Cisco123`
3. Проверить: получил ли IP (должен из пула WIRELESS: 192.168.20.21+)

---

## Проверка всего

```cisco
! === L3 коммутатор ===
show ip route           ! видит все VLAN сети
show ip dhcp binding    ! кому выданы адреса
show vlan brief         ! все VLAN активны
show interfaces trunk   ! trunk порты
show ip ssh             ! SSH включён v2

! === L2 коммутатор ===
show vlan brief
show mac address-table  ! таблица MAC

! === WLC (GUI) ===
Monitor → Summary → APs → Online: 1
Monitor → Clients → должны быть 3 клиента
```

### Проверка связи (ping):

```
! Laptop-PT wireless → ping 192.168.10.1 (шлюз VLAN 10)
! Laptop-PT wired   → ping 192.168.20.1 (шлюз VLAN 20)
! Admin PC → ssh -l admin 192.168.99.2
```

---

## Частые ошибки в этом варианте

| Ошибка | Симптом | Решение |
|---|---|---|
| Забыл `ip routing` на 3650 | Нет маршрутизации между VLAN | `conf t → ip routing` |
| Забыл `ip default-gateway` на 2960 | Нет Telnet/SSH к 2960 | `ip default-gateway 192.168.99.1` |
| Неправильный VLAN на порту к WLC | WLC не получает IP | Проверить `show interfaces trunk` |
| WLAN не включён | Клиенты не видят SSID | WLC → WLAN → ✅ Status Enabled |
| Неверный PSK | Клиент не подключается | Проверить PSK в WLAN Security |
| Неверный crypto key hostname | `crypto key generate rsa` не работает | Сначала `hostname`, потом `ip domain-name` |

---

## Итог

> [!success] Если понял — умеешь:
> - Подключаться через Telnet chain к устройствам без консоли
> - Настраивать SSH и знаешь порядок шагов
> - Настраивать VLAN, trunk, access портов
> - Делать Inter-VLAN на L3 коммутаторе
> - Настраивать WLC WLAN с PSK
> - Подключать wireless клиентов

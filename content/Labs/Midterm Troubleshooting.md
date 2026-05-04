---
  protected: true
---

#labs

# Мидтерм — Troubleshooting кейсы

> [!abstract] Суть
> Все кейсы отсортированы по вероятности появления на мидтерме (★★★★★ = почти точно, ★☆☆☆☆ = маловероятно). Для каждого: симптом → диагноз → команды исправления.

---

## ★★★★★ Очень высокая вероятность

---

### TRBL-01 — Port Security: порт в err-disabled

**Симптом:** Оранжевый порт в Packet Tracer. Нет пинга от ноутбука или сервера.

**Диагноз:**
```
show port-security
show port-security interface fa0/1
show interfaces fa0/1 status
```

Смотри поле `Port Status: Secure-shutdown` и `Last Source Address` — это MAC который пытался подключиться.

**Решение — если MAC известен (static):**
```
interface fastEthernet 0/1
 shutdown
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address XXXX.XXXX.XXXX
exit
write memory
```

**Решение — если MAC неизвестен (sticky):**
```
interface fastEthernet 0/1
 shutdown
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address sticky
exit
write memory
```

> [!danger] Порядок команд
> `maximum` → потом `mac-address`. Иначе: "maximum limit reached" ошибка.

> [!tip] Как узнать MAC
> `show port-security` → колонка **Last Source Address** — MAC устройства которое пытается подключиться.

---

### TRBL-02 — Нет связи между VLAN

**Симптом:** Laptop в VLAN10 не пингует Laptop в VLAN20. Внутри VLAN пинг работает.

**Диагноз:**
```
show ip route
show ip interface brief
show interfaces trunk
show vlan brief
```

**Возможные причины и решения:**

| Причина | Признак | Исправление |
|---|---|---|
| Нет сабинтерфейса на R1 | `show ip route` — нет маршрута к VLAN | Создать `interface Gi0/0.10` с `encapsulation dot1Q 10` |
| Главный интерфейс down | `Gi0/0` → `administratively down` | `interface Gi0/0` → `no shutdown` |
| Trunk не настроен | `show interfaces trunk` — пусто | `switchport mode trunk` на порту к роутеру |
| VLAN не в allowed list | Trunk есть, но VLAN нет | `switchport trunk allowed vlan add 10,20,30` |
| На L3 свиче нет `ip routing` | `show ip route` → только connected | `ip routing` в config terminal |

**Исправление сабинтерфейса:**
```
interface gigabitEthernet 0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
 no shutdown
exit

interface gigabitEthernet 0/0
 no shutdown
exit
```

---

### TRBL-03 — DHCP не выдаёт адреса

**Симптом:** Ноутбук настроен на DHCP но получает `169.254.X.X` (APIPA) или вообще нет IP.

**Диагноз:**
```
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
show running-config | section dhcp
```

**Возможные причины и решения:**

| Причина | Признак | Исправление |
|---|---|---|
| Нет пула DHCP | `show ip dhcp pool` — пусто | Создать `ip dhcp pool VLAN10` |
| Все адреса excluded | Конфигурация excluded слишком широкая | Уменьшить `ip dhcp excluded-address` диапазон |
| Клиент в другой сети, нет relay | DHCP сервер в другом VLAN | Добавить `ip helper-address X.X.X.X` на интерфейс смотрящий в VLAN клиента |
| Конфликт адресов | `show ip dhcp conflict` — есть записи | `clear ip dhcp conflict *` |

**Добавить ip helper-address:**
```
interface gigabitEthernet 0/0.10
 ip helper-address 10.0.99.100
exit
```

**Создать пул:**
```
ip dhcp excluded-address 10.0.10.1 10.0.10.20
ip dhcp pool VLAN10
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 8.8.8.8
exit
```

---

### TRBL-04 — HSRP не работает / неправильный Active

**Симптом:** DSW2 стал Active вместо DSW1. Или оба показывают Standby/Init.

**Диагноз:**
```
show standby brief
show standby
```

Смотри: State (Active/Standby/Init), Priority, Virtual IP.

**Возможные причины и решения:**

| Причина | Признак | Исправление |
|---|---|---|
| Разные virtual IP | Один из свичей в Init | Убедиться что `standby 1 ip X.X.X.X` одинаковый на обоих |
| Нет `preempt` на DSW1 | DSW2 стал Active и держится | Добавить `standby 1 preempt` на DSW1 |
| Неправильный priority | DSW2 priority 110, DSW1 100 | DSW1: `standby 1 priority 110` |
| Разные group номера | Устройства не видят друг друга | Убедиться что group (1) одинаковая |
| SVI interface down | `show ip interface brief` — vlan X down | `interface vlan X` → `no shutdown` |

**Исправление на DSW1:**
```
interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 110
 standby 1 preempt
exit
```

---

## ★★★★☆ Высокая вероятность

---

### TRBL-05 — OSPF соседи не поднимаются

**Симптом:** `show ip ospf neighbor` — пустой список или состояние EXSTART/EXCHANGE.

**Диагноз:**
```
show ip ospf neighbor
show ip ospf interface
show running-config | section ospf
```

**Возможные причины и решения:**

| Причина | Признак | Исправление |
|---|---|---|
| Разные area | Neighbour не появляется вообще | Убедиться что оба используют `area 0` |
| Сеть не добавлена в OSPF | Интерфейс есть, сосед нет | Добавить `network X.X.X.X wildcard area 0` |
| Интерфейс down | `show ip int brief` — down | `no shutdown` на интерфейсе |
| OSPF process не запущен | Нет `router ospf` в конфиге | `router ospf 1` → добавить network |
| Разные Hello/Dead timers | Редко в PT, но бывает | `ip ospf hello-interval` / `ip ospf dead-interval` |

**Исправление:**
```
router ospf 1
 network 10.0.10.0 0.0.0.255 area 0
 network 10.0.12.0 0.0.0.3 area 0
exit
```

---

### TRBL-06 — Hostname не задан или неправильный

**Симптом:** Устройство показывает `Router>` или `Switch>` вместо `R1>`.

**Исправление:**
```
enable
configure terminal
hostname R1
end
```

> [!note] Проверка
> Приглашение меняется мгновенно. `show running-config | include hostname`

---

### TRBL-07 — Trunk не пропускает нужные VLAN

**Симптом:** VLAN создан, порты назначены, но пинг между устройствами в разных коммутаторах не работает.

**Диагноз:**
```
show interfaces trunk
show vlan brief
```

Смотри колонку `VLANs allowed and active in management domain`.

**Исправление:**
```
interface gigabitEthernet 0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
exit
```

Если VLAN уже есть и надо добавить:
```
switchport trunk allowed vlan add 30
```

> [!warning] `allowed vlan` сбрасывает список!
> Команда `switchport trunk allowed vlan 30` **заменяет** список на только VLAN 30.
> Используй `add` чтобы добавить к существующим.

---

### TRBL-08 — Нет доступа по Telnet/SSH

**Симптом:** `telnet 10.0.1.10` → `Connection refused` или `% Connection timed out`.

**Диагноз:**
```
show running-config | section line vty
show ip interface brief
```

**Возможные причины:**

| Причина | Исправление |
|---|---|
| Нет пароля на VTY | `line vty 0 4` → `password cisco` → `login` |
| `login local` но нет user | `username admin secret cisco` |
| `transport input none` | `transport input telnet ssh` |
| IP недоступен (нет маршрута) | Проверить `show ip route`, добавить маршрут |

**Исправление:**
```
line vty 0 4
 password cisco
 login
 transport input telnet ssh
exit
```

---

## ★★★☆☆ Средняя вероятность

---

### TRBL-09 — IPv6 не работает

**Симптом:** Ping по IPv6 адресу не проходит.

**Диагноз:**
```
show ipv6 interface brief
show ipv6 route
```

**Возможные причины:**

| Причина | Исправление |
|---|---|
| Нет `ipv6 unicast-routing` | `ipv6 unicast-routing` в global config |
| Нет IPv6 адреса на интерфейсе | `ipv6 address 2001:DB8:10::1/64` |
| Интерфейс down | `no shutdown` |
| Нет маршрута | `ipv6 route ::/0 next-hop` |

---

### TRBL-10 — NAT не работает (нет выхода в интернет)

**Симптом:** Внутренние устройства не пингуют внешние IP (ISP, интернет).

**Диагноз:**
```
show ip nat translations
show ip nat statistics
show running-config | section nat
```

**Возможные причины:**

| Причина | Исправление |
|---|---|
| Нет `ip nat inside` / `ip nat outside` | Назначить на правильные интерфейсы |
| ACL не включает нужные сети | Проверить `access-list 1` |
| Нет default route | `ip route 0.0.0.0 0.0.0.0 [ISP IP]` |

**Исправление:**
```
interface gigabitEthernet 0/0
 ip nat inside
exit

interface gigabitEthernet 0/1
 ip nat outside
exit

access-list 1 permit 10.0.0.0 0.255.255.255
ip nat inside source list 1 interface Gi0/1 overload
ip route 0.0.0.0 0.0.0.0 192.168.1.1
```

---

### TRBL-11 — ACL блокирует нужный трафик

**Симптом:** Некоторый трафик не проходит хотя маршрутизация правильная.

**Диагноз:**
```
show ip access-lists
show ip interface [int] (смотри "inbound/outbound access list")
```

**Возможные причины:**

| Причина | Исправление |
|---|---|
| Нет `permit any` в конце | Добавить `permit ip any any` в конец ACL |
| ACL применён не на тот интерфейс | `no ip access-group` старый, применить правильно |
| Неправильное направление (in/out) | Поменять `in` на `out` или наоборот |

---

### TRBL-12 — L3 коммутатор не маршрутизирует

**Симптом:** 3650 (DSW) подключён ко всем VLAN но пинги между VLAN не работают.

**Диагноз:**
```
show ip route
show running-config | include ip routing
```

**Исправление:**
```
ip routing
```

> [!danger] Самая частая ошибка на 3650
> Забыли `ip routing` — без этой команды L3 свич работает как обычный L2 коммутатор.

---

### TRBL-13 — STP блокирует нужный порт

**Симптом:** Связь между коммутаторами не работает при наличии нескольких uplink соединений. Порт в BLK состоянии.

**Диагноз:**
```
show spanning-tree
show spanning-tree vlan 10
```

**Исправление — назначить правильный Root Bridge:**
```
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary
```

Или принудительно:
```
spanning-tree vlan 10 priority 4096
```

---

## ★★☆☆☆ Низкая вероятность

---

### TRBL-14 — EtherChannel не поднимается

**Симптом:** `show etherchannel summary` показывает `(I)` — individual порты, не объединённые.

**Диагноз:**
```
show etherchannel summary
show interfaces port-channel 1
```

**Причины:**
- Разные режимы: один `active`, второй `on` → конфликт
- Разные скорости/duplex на портах
- Разные VLAN/trunk настройки

**Исправление:**
```
interface range gi0/1 - 2
 no channel-group
 channel-group 1 mode active
exit
```

---

### TRBL-15 — Serial интерфейс down

**Симптом:** Serial0/0/0 → `Serial0/0/0 is down, line protocol is down`.

**Исправление:**
```
interface serial 0/0/0
 ip address 10.0.12.1 255.255.255.252
 clock rate 64000
 no shutdown
exit
```

> [!tip] clock rate только на DCE стороне
> `show controllers serial 0/0/0` — если видишь `DCE` — значит эта сторона, ставь `clock rate`.

---

## Быстрый диагностический алгоритм

```
Нет пинга?
│
├── ping внутри VLAN не работает?
│   └── Проверь: port security, access vlan, физический кабель
│
├── ping между VLAN не работает?
│   └── Проверь: trunk, Inter-VLAN routing (сабинтерфейсы/SVI), ip routing
│
├── ping до роутера работает, дальше нет?
│   └── Проверь: ip route / OSPF соседи / default-information originate
│
└── ping до ISP/интернет не работает?
    └── Проверь: NAT (inside/outside), default route, ACL
```

---

## Полная таблица show команд для диагностики

| Команда | Что показывает |
|---|---|
| `show ip interface brief` | Все интерфейсы, IP, статус Up/Down |
| `show interfaces status` | L2 статус портов, VLAN, скорость |
| `show vlan brief` | Все VLAN и access порты |
| `show interfaces trunk` | Trunk порты и разрешённые VLAN |
| `show ip route` | Таблица маршрутизации |
| `show ip ospf neighbor` | OSPF соседи и их состояние |
| `show standby brief` | HSRP группы, роли, виртуальный IP |
| `show port-security` | Port Security на всех портах |
| `show ip dhcp binding` | Выданные DHCP адреса |
| `show ip nat translations` | Активные NAT трансляции |
| `show spanning-tree` | STP топология, Root Bridge, роли портов |
| `show etherchannel summary` | Состояние EtherChannel |
| `show running-config` | Полная текущая конфигурация |
| `show startup-config` | Сохранённая конфигурация |
| `show version` | Модель, IOS версия, uptime |
| `show cdp neighbors` | Соседние Cisco устройства |
| `show mac address-table` | MAC адреса и к каким портам привязаны |
| `show arp` | ARP таблица (IP → MAC) |

> [!success] Итог
> Видишь проблему → определи слой (L1/L2/L3) → используй нужную `show` команду → найди причину → исправь → проверь `ping`.

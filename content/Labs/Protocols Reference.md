---
  protected: true
---

#labs

# Протоколы — Полный справочник

> [!abstract] Зачем этот файл
> Преподаватель сказал что пароли на консоль могут быть **именем протокола**. Здесь все сетевые протоколы: название, описание, порт, специфические данные и вероятность встречи на мидтерме.

> [!warning] Пробуй эти пароли если консоль защищена
> Имя протокола строчными буквами: `ospf`, `hsrp`, `vlan`, `cisco`, `telnet`, `ssh`, `dhcp`, `ftp`, `http`, `eigrp`, `stp`, `vtp`, `nat`, `icmp`, `arp`

---

## Протоколы — топ кандидаты для паролей

| Пароль | Вероятность | Почему |
|---|---|---|
| `cisco` | ★★★★★ | Стандартный пароль в лабах |
| `ospf` | ★★★★☆ | Главный протокол маршрутизации в топологии |
| `hsrp` | ★★★★☆ | Тема мидтерма (DSW1/DSW2) |
| `vlan` | ★★★★☆ | Основная тема |
| `telnet` | ★★★☆☆ | Используется для доступа |
| `dhcp` | ★★★☆☆ | Тема мидтерма |
| `ssh` | ★★★☆☆ | Протокол доступа |
| `ftp` | ★★☆☆☆ | Как в Lab7 |
| `eigrp` | ★★☆☆☆ | Cisco протокол |
| `stp` | ★★☆☆☆ | Протокол коммутаторов |
| `class` | ★★☆☆☆ | Второй стандартный пароль в лабах |
| `enable` | ★★☆☆☆ | Иногда используют |
| `icmp` | ★★☆☆☆ | Базовый протокол |
| `nat` | ★★☆☆☆ | Тема мидтерма |
| `arp` | ★★☆☆☆ | Базовый протокол |

---

## L2 — Протоколы канального уровня

---

### STP — Spanning Tree Protocol

**Описание:** Предотвращает петли в сети при избыточных L2 соединениях. Блокирует лишние порты. #abbreviation

**Стандарт:** 802.1D (классический), 802.1W (RSTP), 802.1S (MSTP)

**Cisco версии:**

| Версия | Команда | Описание |
|---|---|---|
| PVST+ | `spanning-tree mode pvst` | Per-VLAN STP (Cisco) |
| Rapid PVST+ | `spanning-tree mode rapid-pvst` | Быстрое сходство |
| MST | `spanning-tree mode mst` | Группы VLAN |

**Таймеры:**

| Таймер | Default | Описание |
|---|---|---|
| Hello | 2 сек | Как часто Root Bridge шлёт BPDU |
| Forward Delay | 15 сек | Время в Listening и Learning |
| Max Age | 20 сек | Время хранения BPDU |

**Роли портов:** Root Port / Designated Port / Alternate (Blocked)

**Специфика:** Root Bridge выбирается по наименьшему Bridge ID = Priority (default 32768) + MAC адрес.

---

### VTP — VLAN Trunking Protocol

**Описание:** Cisco протокол для синхронизации VLAN базы между коммутаторами. #abbreviation

**Порт:** Нет отдельного порта — передаётся через trunk (802.1Q)

**Режимы:**

| Режим | Описание |
|---|---|
| Server | Создаёт/удаляет VLAN, распространяет |
| Client | Получает VLAN от Server, не может изменять |
| Transparent | Не участвует, пересылает VTP сообщения дальше |

**Специфика:**
- VTP Domain name должен совпадать
- VTP password должен совпадать (если настроен)
- Revision number — коммутатор с наибольшим revision перезаписывает остальных

> [!danger] VTP ловушка
> Подключение нового коммутатора с высоким revision number может **стереть все VLAN** на остальных. Используй Transparent режим если не нужна синхронизация.

---

### CDP — Cisco Discovery Protocol

**Описание:** Cisco проприетарный протокол обнаружения соседних устройств. Работает на L2. #abbreviation

**Порт:** Нет (L2, Multicast 01:00:0C:CC:CC:CC)

**Команды:**
```
show cdp neighbors
show cdp neighbors detail
no cdp run                 (отключить глобально)
no cdp enable              (отключить на интерфейсе)
```

---

### LLDP — Link Layer Discovery Protocol

**Описание:** Открытый стандарт 802.1AB — аналог CDP. #abbreviation

```
lldp run
show lldp neighbors
```

---

### ARP — Address Resolution Protocol

**Описание:** Преобразует IP адрес в MAC адрес. Broadcast запрос → unicast ответ. #abbreviation

**Порт:** Нет (L2)

**Работа:** Устройство шлёт broadcast "Кто имеет IP X.X.X.X?" → владелец отвечает своим MAC.

```
show arp
clear arp-cache
arp -a                     (на Windows/Linux)
```

**ARP таблица хранится:** на роутерах и конечных устройствах. MAC таблица хранится на коммутаторах.

---

### 802.1Q — VLAN Trunking

**Описание:** Стандарт тегирования VLAN трафика на trunk портах. Добавляет 4-байтный тег в Ethernet заголовок. #networkterm

**Специфика:**
- Native VLAN = VLAN без тега (default VLAN 1)
- Тег содержит: TPID (0x8100) + Priority (3 бит) + VLAN ID (12 бит)
- Максимум 4094 VLAN

---

## L3 — Протоколы сетевого уровня

---

### ICMP — Internet Control Message Protocol

**Описание:** Служебный протокол IP сети. Используется для ping и traceroute. #abbreviation

**Порт:** Нет (IP Protocol 1)

**Типы сообщений:**

| Тип | Код | Описание |
|---|---|---|
| 0 | 0 | Echo Reply (ответ на ping) |
| 3 | 0 | Network Unreachable |
| 3 | 1 | Host Unreachable |
| 3 | 3 | Port Unreachable |
| 5 | 0 | Redirect |
| 8 | 0 | Echo Request (ping) |
| 11 | 0 | TTL Exceeded (traceroute) |

**Символы ping:**
| Символ | Значение |
|---|---|
| `!` | Echo Reply получен |
| `.` | Таймаут |
| `U` | Destination Unreachable |
| `N` | Network Unreachable |
| `P` | Protocol Unreachable |
| `Q` | Source Quench |

---

### OSPF — Open Shortest Path First

**Описание:** Link-State протокол маршрутизации. Использует алгоритм Дейкстры (SPF). #abbreviation

**Порт:** IP Protocol 89 (не TCP/UDP)

**Multicast адреса:**
- `224.0.0.5` — все OSPF роутеры
- `224.0.0.6` — DR/BDR роутеры

**Hello таймеры:**

| Тип сети | Hello | Dead |
|---|---|---|
| Broadcast / Point-to-Point | 10 сек | 40 сек |
| NBMA | 30 сек | 120 сек |

**Состояния соседства:** Down → Init → 2-Way → Exstart → Exchange → Loading → **Full**

**DR/BDR выбор:** На broadcast сетях выбирается DR (Designated Router) и BDR. Наивысший priority → наивысший Router-ID.

**Специфика:**
- Router-ID = наибольший loopback IP (если есть), иначе наибольший active интерфейс IP
- Wildcard маска = инверсия subnet маски: /24 → 0.0.0.255
- Administrative Distance = 110

```
router ospf 1
 router-id 1.1.1.1
 network 10.0.10.0 0.0.0.255 area 0
 passive-interface gigabitEthernet 0/0
 default-information originate
```

`passive-interface Gi0/0` #ciscoIOScommand Останавливает отправку OSPF Hello на интерфейс. Используй на портах к конечным устройствам.

---

### EIGRP — Enhanced Interior Gateway Routing Protocol

**Описание:** Cisco проприетарный протокол маршрутизации (ранее). Гибридный (Distance Vector + Link State). #abbreviation

**Порт:** IP Protocol 88

**Multicast:** `224.0.0.10`

**Administrative Distance:** Internal = 90, External = 170

**Метрика:** Bandwidth + Delay (по умолчанию)

```
router eigrp 1
 network 10.0.10.0 0.0.0.255
 no auto-summary
```

---

### RIP — Routing Information Protocol

**Описание:** Простой Distance Vector протокол. Устарел, используется редко. #abbreviation

**Порт:** UDP 520

**Версии:** RIPv1 (classful, broadcast), RIPv2 (classless, multicast 224.0.0.9)

**Max hops:** 15 (16 = недостижимо)

**Administrative Distance:** 120

```
router rip
 version 2
 network 10.0.0.0
 no auto-summary
```

---

### BGP — Border Gateway Protocol

**Описание:** Протокол маршрутизации между автономными системами (AS). Протокол интернета. #abbreviation

**Порт:** TCP 179

**Специфика:**
- Единственный EGP в реальном интернете
- Path Vector протокол
- Administrative Distance: eBGP = 20, iBGP = 200

---

### HSRP — Hot Standby Router Protocol

**Описание:** Cisco FHRP протокол. Один виртуальный IP делят два или более роутера/L3 свича. #abbreviation

**Порт:** UDP 1985

**Multicast:** `224.0.0.2` (HSRPv1), `224.0.0.102` (HSRPv2)

**Версии:**

| Версия | Group range | Multicast | Virtual MAC |
|---|---|---|---|
| v1 | 0–255 | 224.0.0.2 | 0000.0C07.ACxx |
| v2 | 0–4095 | 224.0.0.102 | 0000.0C9F.Fxxx |

**Таймеры:** Hello = 3 сек, Hold = 10 сек

**Состояния:** Initial → Learn → Listen → Speak → **Standby** / **Active**

**Специфика:**
- Виртуальный MAC = 0000.0C07.AC**xx** где xx = group number (hex)
- Default priority = 100, Active = наибольший priority
- preempt = вернуть роль Active после восстановления

---

### VRRP — Virtual Router Redundancy Protocol

**Описание:** Открытый стандарт FHRP — аналог HSRP (802.3768). #abbreviation

**Порт:** IP Protocol 112

**Multicast:** `224.0.0.18`

**Отличие от HSRP:** Master/Backup вместо Active/Standby. Default priority = 100. Виртуальный MAC = 0000.5E00.01xx.

---

### GLBP — Gateway Load Balancing Protocol

**Описание:** Cisco FHRP с балансировкой нагрузки. Несколько роутеров активно участвуют одновременно. #abbreviation

**Порт:** UDP 3222

**Специфика:** AVG (Active Virtual Gateway) + AVF (Active Virtual Forwarder). Один virtual IP, разные virtual MAC для балансировки.

---

### NAT — Network Address Translation

**Описание:** Преобразование IP адресов. Позволяет приватным сетям выходить в интернет через один публичный IP. #abbreviation

**Типы:**

| Тип | Описание |
|---|---|
| Static NAT | 1:1 映射 приватного на публичный |
| Dynamic NAT | Пул публичных IP |
| PAT (Overload) | Много:1, разделение по портам |

**Приватные диапазоны (RFC 1918):**
- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

---

## L4 — Транспортный уровень

---

### TCP — Transmission Control Protocol

**Описание:** Надёжный, connection-oriented протокол. Гарантирует доставку и порядок пакетов. #abbreviation

**Порт:** N/A (транспортный протокол)

**3-way handshake:** SYN → SYN-ACK → ACK

**4-way termination:** FIN → ACK → FIN → ACK

**Флаги:** SYN, ACK, FIN, RST, PSH, URG

**Окно (Window):** Управляет потоком данных (flow control).

---

### UDP — User Datagram Protocol

**Описание:** Быстрый, connectionless протокол. Нет гарантии доставки. #abbreviation

**Порт:** N/A

**Используют:** DNS, DHCP, TFTP, VoIP, видеострим, SNMP, RIP, OSPF Hello (нет — OSPF использует IP напрямую).

---

## Прикладные протоколы и их порты

| Протокол | Порт | Транспорт | Описание |
|---|---|---|---|
| **FTP** | 20 (данные), 21 (управление) | TCP | Передача файлов |
| **SSH** | 22 | TCP | Зашифрованный удалённый доступ |
| **Telnet** | 23 | TCP | Незашифрованный удалённый доступ |
| **SMTP** | 25 | TCP | Отправка email |
| **DNS** | 53 | UDP (TCP для zone transfer) | Разрешение имён в IP |
| **DHCP** | 67 (сервер), 68 (клиент) | UDP | Автовыдача IP адресов |
| **TFTP** | 69 | UDP | Простая передача файлов (без аутентификации) |
| **HTTP** | 80 | TCP | Веб страницы |
| **POP3** | 110 | TCP | Получение email |
| **IMAP** | 143 | TCP | Получение email (с сервера) |
| **SNMP** | 161 (запросы), 162 (traps) | UDP | Управление сетевыми устройствами |
| **HTTPS** | 443 | TCP | Зашифрованный HTTP (TLS/SSL) |
| **SMB** | 445 | TCP | Общий доступ к файлам (Windows) |
| **SMTPS** | 465 | TCP | SMTP с шифрованием |
| **LDAP** | 389 | TCP/UDP | Служба каталогов |
| **RDP** | 3389 | TCP | Remote Desktop Protocol |
| **NTP** | 123 | UDP | Синхронизация времени |
| **Syslog** | 514 | UDP | Логирование событий |
| **RADIUS** | 1812 (auth), 1813 (acct) | UDP | AAA аутентификация |
| **TACACS+** | 49 | TCP | Cisco AAA (шифрованный) |
| **BGP** | 179 | TCP | Маршрутизация между AS |
| **OSPF** | — | IP Protocol 89 | Динамическая маршрутизация |
| **EIGRP** | — | IP Protocol 88 | Cisco маршрутизация |
| **GRE** | — | IP Protocol 47 | Туннелирование |
| **IPsec ESP** | — | IP Protocol 50 | VPN шифрование |
| **IPsec AH** | — | IP Protocol 51 | VPN аутентификация |
| **HSRP** | 1985 | UDP | Cisco FHRP |
| **VRRP** | — | IP Protocol 112 | FHRP открытый стандарт |

---

## Специфические данные протоколов

### Диапазоны VLAN

| Диапазон | Тип |
|---|---|
| 0, 4095 | Зарезервированы |
| 1 | Default VLAN (нельзя удалить) |
| 2–1001 | Обычные VLAN |
| 1002–1005 | Зарезервированы (FDDI, Token Ring) |
| 1006–4094 | Extended VLAN (только при VTP Transparent или v3) |

### Administrative Distance (AD) — приоритет маршрутов

| Источник маршрута | AD |
|---|---|
| Connected (прямое подключение) | 0 |
| Static route | 1 |
| EIGRP Summary | 5 |
| eBGP | 20 |
| EIGRP Internal | 90 |
| OSPF | 110 |
| IS-IS | 115 |
| RIP | 120 |
| EIGRP External | 170 |
| iBGP | 200 |
| Unknown | 255 (не используется) |

### Важные Multicast адреса

| Адрес | Для кого |
|---|---|
| `224.0.0.1` | Все узлы в сегменте |
| `224.0.0.2` | Все роутеры / HSRPv1 |
| `224.0.0.5` | Все OSPF роутеры |
| `224.0.0.6` | OSPF DR/BDR |
| `224.0.0.9` | RIPv2 роутеры |
| `224.0.0.10` | EIGRP роутеры |
| `224.0.0.102` | HSRPv2 / VRRP |

### IPv6 специальные адреса

| Адрес | Описание |
|---|---|
| `::1/128` | Loopback (аналог 127.0.0.1) |
| `fe80::/10` | Link-Local (автоматический, только в сегменте) |
| `fc00::/7` | Unique Local (аналог RFC1918) |
| `2000::/3` | Global Unicast (публичные IPv6) |
| `ff02::1` | All nodes multicast |
| `ff02::2` | All routers multicast |
| `ff02::5` | OSPFv3 all routers |
| `ff02::6` | OSPFv3 DR/BDR |

### EtherType значения

| EtherType | Протокол |
|---|---|
| `0x0800` | IPv4 |
| `0x0806` | ARP |
| `0x8100` | 802.1Q VLAN тег |
| `0x86DD` | IPv6 |
| `0x8847` | MPLS |

> [!success] Итог
> Запомни топ паролей: `cisco`, `class`, `ospf`, `hsrp`, `vlan`, `telnet`, `dhcp`.
> Запомни ключевые порты: SSH=22, Telnet=23, DNS=53, DHCP=67/68, HTTP=80, HTTPS=443, FTP=21.

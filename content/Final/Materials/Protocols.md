---
tags:
  - финал
  - протоколы
---

# Протоколы - Быстрое повторение

> [!tip] Стратегия
> Для каждого протокола знай: **уровень OSI → что делает → порт/транспорт → ключевая особенность**.

---

## Прикладной уровень (Layer 7) - Application

### DNS - Domain Name System
- **Порт:** UDP 53 (TCP при zone transfer или ответах >512 байт)
- **Что делает:** Переводит доменные имена (`cisco.com`) в IP-адреса
- **Иерархия:** Root → TLD (`.com`, `.org`) → Authoritative DNS
- **Типы записей:** A (IPv4), AAAA (IPv6), MX (почта), CNAME (псевдоним), PTR (обратный lookup)

### HTTP / HTTPS
- **HTTP:** TCP 80 - передача веб-страниц, **открытый текст**
- **HTTPS:** TCP/UDP 443 - HTTP + **TLS/SSL шифрование**
- **Методы:** GET (запросить), POST (отправить форму), PUT (загрузить файл)
- **Коды ответа:** 200 OK, 301 Redirect, 404 Not Found, 500 Server Error

### FTP - File Transfer Protocol
- **Порт:** TCP **21** (управление) + TCP **20** (данные)
- **Два соединения:** Control (постоянное) + Data (открывается для каждой передачи)
- **Особенность:** Нет шифрования. SFTP (TCP 22) - FTP через SSH, зашифрованный

### TFTP - Trivial File Transfer Protocol
- **Порт:** UDP 69
- **Особенность:** Без аутентификации, без надёжности. Используется для загрузки IOS-образов, конфигураций на сетевые устройства

### SMTP - Simple Mail Transfer Protocol
- **Порт:** TCP 25
- **Что делает:** **Отправка** email - от клиента на сервер и между серверами
- **Принцип:** Store-and-forward (сохраняет и пересылает). Если сервер недоступен - ставит в очередь (spool)

### POP3 - Post Office Protocol v3
- **Порт:** TCP 110
- **Что делает:** **Получение** email - скачивает письма **и удаляет с сервера**
- **Минус:** Нет синхронизации между устройствами

### IMAP - Internet Message Access Protocol
- **Порт:** TCP 143
- **Что делает:** Доступ к письмам **прямо на сервере** (письма не удаляются)
- **Плюс:** Синхронизация между устройствами, папки на сервере

### DHCP - Dynamic Host Configuration Protocol
- **Порты:** UDP 67 (сервер) / 68 (клиент)
- **Что делает:** Автоматически выдаёт IP, маску, шлюз, DNS хостам
- **Процесс DORA:** Discover → Offer → Request → Acknowledge
- **Аренда:** IP выдаётся на время (lease time). По истечении - обновляется или возвращается в пул
- **relay agent:** Если DHCP-сервер в другом VLAN - роутер пересылает DHCP-запросы (`ip helper-address`)

### SNMP - Simple Network Management Protocol
- **Порты:** UDP 161 (запросы), UDP 162 (traps - уведомления)
- **Версии:** SNMPv1, v2c (community string), **v3** (шифрование + аутентификация)
- **Компоненты:** Manager (NMS) + Agent (на устройстве) + MIB (база данных объектов)
- **Операции:** GET, SET, TRAP

### NTP - Network Time Protocol
- **Порт:** UDP 123
- **Что делает:** Синхронизирует время на всех устройствах
- **Stratum:** Уровень точности. Stratum 0 = атомные часы, Stratum 1 = подключён к Stratum 0. Чем выше цифра - менее точно

### Syslog
- **Порт:** UDP 514
- **Что делает:** Отправляет системные сообщения/логи на centralized syslog-сервер
- **Уровни severity (0–7):** 0=Emergency, 1=Alert, 2=Critical, 3=Error, 4=Warning, 5=Notice, 6=Info, **7=Debug**

### SMB - Server Message Block
- **Порт:** TCP 445
- **Что делает:** Общий доступ к файлам, папкам, принтерам (Windows). Долгосрочное соединение
- **Linux:** SAMBA - реализация SMB для Linux/Unix

---

## Транспортный уровень (Layer 4) - Transport

### TCP - Transmission Control Protocol
- **Тип:** Connection-Oriented (устанавливает соединение перед передачей)
- **Гарантирует:** Доставку, порядок, контроль потока (flow control)
- **3-way handshake:** SYN → SYN-ACK → ACK
- **4-way teardown:** FIN → ACK → FIN → ACK
- **Флаги:** SYN, ACK, FIN, RST, PSH, URG
- **Использует:** HTTP, HTTPS, FTP, SSH, Telnet, SMTP, POP3, IMAP, BGP

### UDP - User Datagram Protocol
- **Тип:** Connectionless (без установки соединения)
- **Нет:** Гарантии доставки, нет порядка, нет flow control
- **Плюс:** Быстрый, меньше overhead
- **Использует:** DNS, DHCP, TFTP, NTP, Syslog, SNMP, RIP, VoIP, видеострим

---

## Сетевой уровень (Layer 3) - Network / Internet

### IP - Internet Protocol
- **IPv4:** 32-битный адрес, ~4.3 млрд адресов
- **IPv6:** 128-битный адрес, практически неограниченно
- **Connectionless:** Каждый пакет маршрутизируется независимо
- **Best-effort:** Без гарантий доставки (этим занимается TCP)

### ICMP - Internet Control Message Protocol
- **IP Protocol:** 1
- **Порта нет** - работает прямо поверх IP
- **Что делает:** Служебные сообщения. Ping = Echo Request (type 8) + Echo Reply (type 0)
- **Traceroute:** Использует TTL Exceeded (type 11) - каждый hop уменьшает TTL на 1

### OSPF - Open Shortest Path First
- **IP Protocol:** 89 (не TCP/UDP)
- **Тип:** Link-State, алгоритм Дейкстры (SPF)
- **Admin Distance:** 110
- **Multicast:** 224.0.0.5 (все OSPF роутеры), 224.0.0.6 (DR/BDR)
- **Hello таймеры:** Broadcast/P2P = 10 сек / 40 сек Dead; NBMA = 30 сек / 120 сек
- **Состояния:** Down → Init → 2-Way → Exstart → Exchange → Loading → **Full**
- **Router-ID:** наибольший loopback IP → наибольший активный интерфейс

### EIGRP - Enhanced Interior Gateway Routing Protocol
- **IP Protocol:** 88
- **Тип:** Гибридный (Distance Vector + Link-State) - Cisco
- **Admin Distance:** Internal = 90, External = 170
- **Multicast:** 224.0.0.10
- **Метрика:** Bandwidth + Delay (по умолчанию)

### RIP - Routing Information Protocol
- **Порт:** UDP 520
- **Тип:** Distance Vector
- **Admin Distance:** 120
- **Ограничение:** Max 15 hops (16 = недостижимо)
- **v1:** Classful, broadcast; **v2:** Classless, multicast 224.0.0.9

### BGP - Border Gateway Protocol
- **Порт:** TCP 179
- **Тип:** Path Vector - протокол между автономными системами (AS)
- **Admin Distance:** eBGP = 20, iBGP = 200
- **Единственный EGP** в реальном интернете

### NAT - Network Address Translation
- **Static NAT:** 1:1 - один приватный ↔ один публичный
- **Dynamic NAT:** Пул публичных IP
- **PAT (Overload):** Много:1, разделение по портам - самый распространённый вид

---

## Канальный уровень (Layer 2) - Data Link

### ARP - Address Resolution Protocol
- **Порта нет** - L2 протокол
- **Что делает:** IP → MAC. Broadcast запрос "Кто имеет IP X?" → Unicast ответ с MAC
- **ARP table:** Хранится на хостах и роутерах
- **MAC table:** Хранится на коммутаторах

### STP - Spanning Tree Protocol
- **Стандарт:** 802.1D (классический), 802.1W (RSTP - быстрый), 802.1S (MSTP)
- **Что делает:** Предотвращает L2 петли, блокирует избыточные порты
- **Root Bridge:** Наименьший Bridge ID = Priority (32768 default) + MAC
- **Таймеры:** Hello = 2 сек, Forward Delay = 15 сек, Max Age = 20 сек
- **Роли портов:** Root Port, Designated Port, Alternate (Blocked)
- **Cisco:** PVST+ (per-VLAN), Rapid PVST+

### VTP - VLAN Trunking Protocol
- **Передаётся через:** trunk (802.1Q)
- **Режимы:** Server (создаёт/распространяет), Client (получает), Transparent (пересылает, не участвует)
- **Опасность:** Высокий revision number стирает все VLAN на остальных коммутаторах

### CDP - Cisco Discovery Protocol
- **Уровень:** L2, Multicast 01:00:0C:CC:CC:CC
- **Что делает:** Обнаружение соседних Cisco-устройств
- **Cisco-only**, аналог - **LLDP** (802.1AB, открытый стандарт)

### 802.1Q - VLAN Trunking
- **Добавляет 4-байтный тег** в Ethernet фрейм
- **Native VLAN:** VLAN без тега (default = VLAN 1)
- **Max VLAN ID:** 4094

---

## FHRP - First Hop Redundancy Protocols

### HSRP - Hot Standby Router Protocol
- **Порт:** UDP 1985, **Cisco-only**
- **Multicast:** v1 = 224.0.0.2, v2 = 224.0.0.102
- **Состояния:** Initial → Learn → Listen → Speak → Standby → **Active**
- **Таймеры:** Hello = 3 сек, Hold = 10 сек
- **Virtual MAC:** v1 = 0000.0C07.AC**xx**, v2 = 0000.0C9F.F**xxx** (xx = group hex)
- **Приоритет:** Default = 100. Active = наибольший. `preempt` = вернуть Active после восстановления

### VRRP - Virtual Router Redundancy Protocol
- **IP Protocol:** 112, **открытый стандарт** (802.3768)
- **Multicast:** 224.0.0.18
- **Master/Backup** (не Active/Standby как HSRP)
- **Virtual MAC:** 0000.5E00.01**xx**

### GLBP - Gateway Load Balancing Protocol
- **Порт:** UDP 3222, **Cisco-only**
- **Особенность:** Балансировка нагрузки - все роутеры активны одновременно
- **AVG** = Active Virtual Gateway, **AVF** = Active Virtual Forwarder

---

## Безопасность

### SSH vs Telnet

| | SSH | Telnet |
|--|-----|--------|
| Порт | TCP 22 | TCP 23 |
| Шифрование | ✅ Да | ❌ Нет |
| Безопасность | Безопасен | Небезопасен |

### RADIUS vs TACACS+

| | RADIUS | TACACS+ |
|--|--------|---------|
| Порт | UDP 1812/1813 | TCP 49 |
| Шифрование | Только пароль | Весь пакет |
| Разработчик | Открытый стандарт | Cisco |
| AAA | Объединяет Auth+Authz | Разделяет Auth/Authz/Acct |

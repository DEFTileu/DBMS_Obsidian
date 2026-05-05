---
tags:
  - финал
  - порты
---

# Все порты - Шпаргалка для финала

> [!tip] Как учить
> Учи тройками: **Протокол → Порт → Транспорт**. Самые важные: 20/21, 22, 23, 25, 53, 67/68, 69, 80, 110, 143, 161/162, 443.

---

## Полная таблица портов (по номеру)

| Порт     | Протокол                 | Транспорт                                       | Что делает                                                     |
| -------- | ------------------------ | ----------------------------------------------- | -------------------------------------------------------------- |
| **20**   | FTP Data                 | TCP                                             | Передача данных файлов                                         |
| **21**   | FTP Control              | TCP                                             | Управление FTP-сессией (команды)                               |
| **22**   | SSH / SFTP               | TCP                                             | Зашифрованный удалённый доступ / зашифрованная передача файлов |
| **23**   | Telnet                   | TCP                                             | Незашифрованный удалённый доступ                               |
| **25**   | SMTP                     | TCP                                             | Отправка email (сервер → сервер, клиент → сервер)              |
| **37**   | Time                     | TCP/UDP                                         | Синхронизация времени (старый протокол, предшественник NTP)    |
| **43**   | WHOIS                    | TCP                                             | Запрос информации о домене/IP владельце                        |
| **49**   | TACACS / TACACS+         | TCP                                             | Cisco AAA аутентификация (полное шифрование пакета)            |
| **53**   | DNS                      | UDP (TCP при zone transfer и ответах >512 байт) | Перевод доменных имён в IP                                     |
| **67**   | DHCP/BOOTP Server        | UDP                                             | Сервер принимает запросы от клиентов                           |
| **68**   | DHCP/BOOTP Client        | UDP                                             | Клиент отправляет запросы на сервер                            |
| **69**   | TFTP                     | UDP                                             | Простая передача файлов без аутентификации                     |
| **70**   | Gopher                   | TCP                                             | Устаревший протокол передачи документов (до HTTP)              |
| **79**   | Finger                   | TCP                                             | Информация о пользователях на удалённом хосте                  |
| **80**   | HTTP                     | TCP                                             | Веб-страницы (незашифровано)                                   |
| **88**   | Kerberos                 | TCP/UDP                                         | Аутентификация в домене (Windows Active Directory)             |
| **110**  | POP3                     | TCP                                             | Получение email (скачать и удалить с сервера)                  |
| **119**  | NNTP                     | TCP                                             | Network News Transfer Protocol (новостные группы)              |
| **123**  | NTP                      | UDP                                             | Синхронизация времени (современный стандарт)                   |
| **137**  | NetBIOS Name Service     | UDP                                             | Разрешение NetBIOS-имён в IP (аналог DNS для Windows)          |
| **138**  | NetBIOS Datagram Service | UDP                                             | Передача датаграмм (broadcast/multicast в Windows)             |
| **139**  | NetBIOS Session Service  | TCP                                             | Сессии SMB поверх NetBIOS (устаревший путь)                    |
| **143**  | IMAP                     | TCP                                             | Получение email (письма остаются на сервере)                   |
| **161**  | SNMP                     | UDP                                             | Запросы к сетевым устройствам (GET, SET)                       |
| **162**  | SNMP Trap                | UDP                                             | Уведомления от устройств к менеджеру (traps)                   |
| **179**  | BGP                      | TCP                                             | Маршрутизация между автономными системами (интернет)           |
| **194**  | IRC                      | TCP                                             | Internet Relay Chat                                            |
| **389**  | LDAP                     | TCP/UDP                                         | Служба каталогов (Active Directory, запросы)                   |
| **443**  | HTTPS                    | TCP/UDP                                         | Зашифрованный HTTP (TLS/SSL)                                   |
| **445**  | SMB (Direct)             | TCP                                             | Общий доступ к файлам и принтерам напрямую (без NetBIOS)       |
| **465**  | SMTPS                    | TCP                                             | SMTP с шифрованием (устаревший, заменён на 587)                |
| **500**  | IKE / ISAKMP             | UDP                                             | Internet Key Exchange — согласование IPsec VPN                 |
| **514**  | Syslog                   | UDP                                             | Отправка системных логов на centralized сервер                 |
| **520**  | RIP                      | UDP                                             | Протокол маршрутизации RIPv1/v2                                |
| **587**  | SMTP Submission          | TCP                                             | Отправка почты клиентом на сервер (с аутентификацией, TLS)     |
| **636**  | LDAPS                    | TCP                                             | LDAP с шифрованием (TLS)                                       |
| **993**  | IMAPS                    | TCP                                             | IMAP с шифрованием (TLS)                                       |
| **995**  | POP3S                    | TCP                                             | POP3 с шифрованием (TLS)                                       |
| **1701** | L2TP                     | UDP                                             | Layer 2 Tunneling Protocol (VPN туннель)                       |
| **1723** | PPTP                     | TCP                                             | Point-to-Point Tunneling Protocol (VPN, устаревший)            |
| **1812** | RADIUS Auth              | UDP                                             | Аутентификация RADIUS                                          |
| **1813** | RADIUS Acct              | UDP                                             | Учёт (Accounting) RADIUS                                       |
| **1985** | HSRP                     | UDP                                             | Cisco FHRP - виртуальный шлюз                                  |
| **3222** | GLBP                     | UDP                                             | Cisco FHRP с балансировкой нагрузки                            |
| **3389** | RDP                      | TCP                                             | Remote Desktop Protocol (Windows)                              |
| **4500** | IPsec NAT-T              | UDP                                             | IPsec через NAT (NAT Traversal)                                |
| **5246** | CAPWAP Control           | UDP                                             | Управление AP через WLC (контрольный канал)                    |
| **5247** | CAPWAP Data              | UDP                                             | Передача данных между AP и WLC                                 |
| **8080** | HTTP alt                 | TCP                                             | Альтернативный порт для HTTP / веб-прокси                      |
| **8443** | HTTPS alt                | TCP                                             | Альтернативный порт для HTTPS                                  |

---

## Протоколы без TCP/UDP портов (IP Protocol Number)

Эти протоколы работают **напрямую поверх IP**, у них нет TCP/UDP порта.

| IP Protocol # | Протокол | Что делает |
|---------------|----------|------------|
| **1** | ICMP | Ping, traceroute, сообщения об ошибках (IPv4) |
| **6** | TCP | Надёжный транспортный протокол |
| **17** | UDP | Быстрый транспортный протокол без подтверждения |
| **47** | GRE | Туннелирование (Generic Routing Encapsulation) |
| **50** | IPsec ESP | VPN - шифрование данных |
| **51** | IPsec AH | VPN - аутентификация без шифрования данных |
| **58** | ICMPv6 | Ping, NDP, сообщения об ошибках (IPv6) |
| **88** | EIGRP | Cisco протокол маршрутизации |
| **89** | OSPF | Открытый протокол маршрутизации (Link-State) |
| **112** | VRRP | Открытый аналог HSRP |

---

## Диапазоны портов

| Диапазон | Название | Кто использует |
|----------|----------|----------------|
| **0 – 1023** | Well-known (общеизвестные) | Системные сервисы (HTTP, FTP, SSH, DNS...) |
| **1024 – 49151** | Registered (зарегистрированные) | Приложения (RADIUS, RDP, HSRP, CAPWAP...) |
| **49152 – 65535** | Dynamic / Private (динамические) | Клиентские временные порты |

> [!important] Запомни
> **Well-known = 0–1023** — самый частый вопрос на экзаменах. Назначаются организацией **IANA**.

---

## Группировка по функции

### Удалённый доступ
- Telnet = **23** (небезопасный, открытый текст)
- SSH = **22** (зашифрованный)
- RDP = **3389** (Windows Remote Desktop)

### Электронная почта
- SMTP = **25** (отправка сервер↔сервер)
- SMTP Submission = **587** (отправка клиент→сервер, с TLS)
- SMTPS = **465** (устаревший SMTP+TLS)
- POP3 = **110** (получение — удаляет с сервера)
- POP3S = **995** (POP3 + TLS)
- IMAP = **143** (получение — хранит на сервере)
- IMAPS = **993** (IMAP + TLS)

### Передача файлов
- FTP = **20/21** (с подтверждением, TCP)
- SFTP = **22** (FTP через SSH)
- TFTP = **69** (без подтверждения, UDP, для IOS образов)
- SMB = **445** (сетевые папки Windows, напрямую)
- NetBIOS+SMB = **139** (старый путь через NetBIOS)

### DNS и адресация
- DNS = **53** (UDP/TCP)
- DHCP/BOOTP Server = **67** (UDP)
- DHCP/BOOTP Client = **68** (UDP)
- NetBIOS Name = **137** (UDP, разрешение имён Windows)
- WHOIS = **43** (TCP)

### Веб
- HTTP = **80**
- HTTPS = **443**
- HTTP alt = **8080**
- HTTPS alt = **8443**

### Управление сетью
- SNMP запросы = **161** (UDP)
- SNMP Traps = **162** (UDP)
- NTP = **123** (UDP, современный)
- Time = **37** (TCP/UDP, устаревший)
- Syslog = **514** (UDP)
- TACACS+ = **49** (TCP)
- RADIUS Auth = **1812** (UDP)
- RADIUS Acct = **1813** (UDP)

### Служба каталогов
- LDAP = **389** (TCP/UDP)
- LDAPS = **636** (TCP, с TLS)
- Kerberos = **88** (TCP/UDP, аутентификация AD)

### VPN и туннели
- IKE/ISAKMP = **500** (UDP, согласование IPsec)
- IPsec NAT-T = **4500** (UDP, IPsec через NAT)
- GRE = IP Protocol **47**
- IPsec ESP = IP Protocol **50**
- IPsec AH = IP Protocol **51**
- L2TP = **1701** (UDP)
- PPTP = **1723** (TCP, устаревший)

### Маршрутизация
- BGP = **179** (TCP)
- RIP = **520** (UDP)
- OSPF = IP Protocol **89**
- EIGRP = IP Protocol **88**

### FHRP (резервные шлюзы)
- HSRP = **1985** (UDP) — Cisco
- VRRP = IP Protocol **112** — открытый стандарт
- GLBP = **3222** (UDP) — Cisco с балансировкой

### Беспроводные сети (WLAN)
- CAPWAP Control = **5246** (UDP) — управление AP через WLC
- CAPWAP Data = **5247** (UDP) — данные между AP и WLC

### Windows / NetBIOS
- NetBIOS Name Service = **137** (UDP)
- NetBIOS Datagram Service = **138** (UDP)
- NetBIOS Session Service = **139** (TCP)
- SMB = **445** (TCP, прямой, современный)
- RDP = **3389** (TCP)
- Kerberos = **88** (TCP/UDP)
- LDAP = **389** / LDAPS = **636**

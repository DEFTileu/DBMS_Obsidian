---
tags:
  - финал
  - редкаяинформация
---

# Редкая информация - Трудные вопросы финала

> [!warning] Зачем этот файл
> Здесь собраны темы, которые редко встречаются в обычных конспектах, но часто появляются в экзаменах. Организации стандартизации, точные цифры, нюансы протоколов.

---

## Организации стандартизации - часто путают

| Аббревиатура | Полное название | Что делает |
|---|---|---|
| **ICANN** | Internet Corporation for Assigned Names and Numbers | Управляет распределением IP-адресов, доменных имён, AS-номеров в масштабах интернета |
| **IANA** | Internet Assigned Numbers Authority | Подразделение ICANN. Фактически ведёт базы: IP-адреса, порты, протоколы |
| **IETF** | Internet Engineering Task Force | Разрабатывает стандарты интернета (RFC документы). Открытая организация |
| **RFC** | Request for Comments | Документы с техническими стандартами интернета. Публикует IETF. Пример: RFC 791 = IPv4 |
| **IEEE** | Institute of Electrical and Electronics Engineers | Стандарты: Ethernet (802.3), Wi-Fi (802.11), STP (802.1D), VLAN (802.1Q) |
| **ISO** | International Organization for Standardization | Разработала модель OSI (совместно с ITU). Международная организация |
| **ITU** | International Telecommunication Union | Стандарты телекоммуникаций. Совместно с ISO разработала OSI |
| **ISOC** | Internet Society | Продвигает развитие интернета, управляет IETF |

> [!important] Частый вопрос
> - **Кто управляет IP-адресами глобально?** → IANA / ICANN
> - **Кто публикует стандарты интернета?** → IETF (через RFC)
> - **Кто стандартизировал Ethernet и Wi-Fi?** → IEEE
> - **Кто разработал модель OSI?** → ISO (совместно с ITU)

---

## Модель OSI - 7 уровней точно

| # | Уровень | Английский | PDU | Ключевые протоколы |
|---|---------|------------|-----|---------------------|
| 7 | Прикладной | Application | Data | HTTP, FTP, DNS, SMTP |
| 6 | Представления | Presentation | Data | SSL/TLS, шифрование, сжатие |
| 5 | Сеансовый | Session | Data | NetBIOS, RPC, SQL сессии |
| 4 | Транспортный | Transport | Segment | TCP, UDP |
| 3 | Сетевой | Network | Packet | IP, ICMP, OSPF, EIGRP |
| 2 | Канальный | Data Link | Frame | Ethernet, 802.1Q, ARP, STP |
| 1 | Физический | Physical | Bits | Кабели, хабы, сигналы |

> [!note] PDU = Protocol Data Unit - название единицы данных на каждом уровне

**Мнемоника (снизу вверх):** **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way
(Physical → Data Link → Network → Transport → Session → Presentation → Application)

---

## IPv4 - Специальные адреса

| Адрес / Диапазон | Назначение |
|---|---|
| `0.0.0.0` | Текущая сеть / неизвестный адрес источника (при DHCP Discover) |
| `127.0.0.1` | Loopback - тест локального стека (127.0.0.0/8) |
| `169.254.0.0/16` | APIPA - автоматический адрес если DHCP не ответил (Windows) |
| `255.255.255.255` | Limited broadcast - всем устройствам в сегменте |
| `224.0.0.0/4` | Multicast диапазон (224.0.0.0 – 239.255.255.255) |
| `10.0.0.0/8` | Приватный (RFC 1918) |
| `172.16.0.0/12` | Приватный (172.16.0.0 – 172.31.255.255) |
| `192.168.0.0/16` | Приватный (RFC 1918) |

### Классы IPv4 (устаревшие, но могут спросить)

| Класс | Диапазон первого октета | Маска | Назначение |
|-------|------------------------|-------|------------|
| A | 1 – 126 | /8 | Крупные сети |
| B | 128 – 191 | /16 | Средние сети |
| C | 192 – 223 | /24 | Малые сети |
| D | 224 – 239 | - | Multicast |
| E | 240 – 255 | - | Зарезервировано/экспериментальное |

> **127** = loopback (не входит в класс A, зарезервирован)

---

## IPv6 - Важные адреса

| Адрес | Тип | Аналог в IPv4 |
|---|---|---|
| `::1/128` | Loopback | 127.0.0.1 |
| `fe80::/10` | Link-Local | нет прямого аналога |
| `fc00::/7` | Unique Local (ULA) | RFC 1918 (приватные) |
| `2000::/3` | Global Unicast (GUA) | Публичные IP |
| `ff02::1` | All nodes multicast | 224.0.0.1 |
| `ff02::2` | All routers multicast | 224.0.0.2 |
| `ff02::5` | OSPFv3 all routers | 224.0.0.5 |
| `ff02::6` | OSPFv3 DR/BDR | 224.0.0.6 |
| `ff02::1:ff00:0/104` | Solicited-Node multicast | используется NDP (аналог ARP) |

### IPv6 - Нет ARP
В IPv6 вместо ARP используется **NDP (Neighbor Discovery Protocol)** поверх ICMPv6:
- **NS (Neighbor Solicitation)** - аналог ARP Request
- **NA (Neighbor Advertisement)** - аналог ARP Reply
- **RS/RA** - Router Solicitation / Router Advertisement (для SLAAC)

---

## DHCP - Процесс DORA

```
Клиент ──────────────────────── Сервер

  DISCOVER (broadcast)  →        (порт 68 → 67)
                        ←  OFFER (unicast или broadcast)
  REQUEST (broadcast)   →        (клиент подтверждает)
                        ←  ACK   (сервер подтверждает)
```

> [!tip] Почему REQUEST - broadcast?
> Клиент мог получить OFFER от нескольких серверов. Broadcast-REQUEST уведомляет **все** серверы что выбран один, остальные возвращают IP в пул.

**Аренда (lease):** 50% времени аренды клиент пытается обновить у того же сервера (unicast). 87.5% - broadcast-запрос к любому серверу.

---

## DNS - Типы записей

| Запись | Что хранит |
|---|---|
| **A** | Имя → IPv4 адрес |
| **AAAA** | Имя → IPv6 адрес |
| **MX** | Mail exchanger - сервер почты для домена |
| **CNAME** | Псевдоним (alias) для другого имени |
| **PTR** | IP → Имя (обратный lookup) |
| **NS** | Name Server - авторитетный DNS сервер для домена |
| **SOA** | Start of Authority - главный DNS сервер зоны |
| **TXT** | Текстовая запись (SPF, DKIM для почты) |

---

## Стандарты IEEE 802 - полный список

| Стандарт | Что это |
|---|---|
| **802.1D** | STP (Spanning Tree Protocol) |
| **802.1Q** | VLAN тегирование (trunk) |
| **802.1W** | RSTP (Rapid STP) |
| **802.1S** | MSTP (Multiple STP) |
| **802.1X** | Аутентификация на уровне порта (EAP) |
| **802.1AB** | LLDP (Link Layer Discovery Protocol) |
| **802.3** | Ethernet (проводной) |
| **802.3u** | Fast Ethernet (100 Мбит/с) |
| **802.3ab** | Gigabit Ethernet по витой паре (1000BASE-T) |
| **802.3z** | Gigabit Ethernet по оптике |
| **802.3ae** | 10 Gigabit Ethernet |
| **802.11** | Wi-Fi (общий стандарт беспроводных сетей) |
| **802.11a** | Wi-Fi 5 ГГц, до 54 Мбит/с |
| **802.11b** | Wi-Fi 2.4 ГГц, до 11 Мбит/с |
| **802.11g** | Wi-Fi 2.4 ГГц, до 54 Мбит/с |
| **802.11n** | Wi-Fi 2.4/5 ГГц, до 600 Мбит/с (Wi-Fi 4) |
| **802.11ac** | Wi-Fi 5 ГГц, до ~3.5 Гбит/с (Wi-Fi 5) |
| **802.11ax** | Wi-Fi 6/6E, 2.4/5/6 ГГц |
| **802.3af** | PoE - Power over Ethernet (до 15.4 Вт) |
| **802.3at** | PoE+ (до 30 Вт) |

---

## Важные multicast адреса

| Адрес IPv4 | Для кого |
|---|---|
| `224.0.0.1` | Все узлы в сегменте |
| `224.0.0.2` | Все роутеры / **HSRPv1** |
| `224.0.0.5` | Все OSPF роутеры |
| `224.0.0.6` | OSPF DR/BDR |
| `224.0.0.9` | RIPv2 роутеры |
| `224.0.0.10` | EIGRP роутеры |
| `224.0.0.18` | VRRP |
| `224.0.0.102` | **HSRPv2** |

---

## Administrative Distance (AD) - приоритет маршрутов

Чем **меньше AD** - тем **приоритетнее** маршрут.

| Источник | AD |
|---|---|
| Connected (прямое подключение) | **0** |
| Static route | **1** |
| EIGRP Summary route | 5 |
| eBGP | **20** |
| EIGRP Internal | **90** |
| OSPF | **110** |
| IS-IS | 115 |
| RIP | **120** |
| EIGRP External | 170 |
| iBGP | 200 |
| Unknown / не используется | 255 |

---

## EtherType - значения в Ethernet-фрейме

| EtherType | Протокол |
|---|---|
| `0x0800` | IPv4 |
| `0x0806` | ARP |
| `0x8100` | 802.1Q VLAN тег |
| `0x86DD` | IPv6 |
| `0x8847` | MPLS unicast |

---

## VLAN диапазоны

| Диапазон | Тип |
|---|---|
| **0, 4095** | Зарезервированы (нельзя использовать) |
| **1** | Default VLAN - нельзя удалить, нельзя переименовать |
| **2 – 1001** | Normal range VLAN - обычные VLAN |
| **1002 – 1005** | Зарезервированы (FDDI, Token Ring - устаревшие) |
| **1006 – 4094** | Extended VLAN - только при VTP Transparent или VTPv3 |

---

## Spanning Tree - точные цифры

| Таймер | Значение | Что значит |
|---|---|---|
| Hello | **2 сек** | Как часто Root Bridge шлёт BPDU |
| Forward Delay | **15 сек** | Время в Listening и Learning состояниях |
| Max Age | **20 сек** | Время хранения BPDU (если нет обновления - порт меняет состояние) |
| Total convergence | **50 сек** | Полное сходство STP (Blocking → Forwarding) |

### Состояния порта STP:
`Blocking` → `Listening` (15 сек) → `Learning` (15 сек) → `Forwarding`

### RSTP (802.1W) - ускорение:
- Convergence: **1–2 сек** вместо 50
- Роли: Root, Designated, Alternate, **Backup**
- Добавлены **Edge ports** (аналог PortFast) - сразу в Forwarding

---

## Кабели UTP - категории

| Категория | Скорость | Частота | Стандарт Ethernet |
|---|---|---|---|
| Cat 3 | 10 Мбит/с | 16 МГц | 10BASE-T |
| Cat 5 | 100 Мбит/с | 100 МГц | 100BASE-TX |
| Cat 5e | 1 Гбит/с | 100 МГц | 1000BASE-T |
| Cat 6 | 1 Гбит/с (10G на короткие) | 250 МГц | 10GBASE-T (до 55 м) |
| Cat 6a | 10 Гбит/с | 500 МГц | 10GBASE-T (до 100 м) |

### Типы подключений:
- **Straight-through** - разные устройства (PC → Switch, Switch → Router)
- **Crossover** - одинаковые устройства (Switch → Switch, PC → PC)
- **Rollover (Console)** - PC → Console port роутера/свича (синий кабель Cisco)

> [!note] Современные устройства с Auto-MDIX определяют тип кабеля автоматически

---

## Wireless - Wi-Fi детали

| Стандарт | Частота | Макс. скорость | Особенность |
|---|---|---|---|
| 802.11a | 5 ГГц | 54 Мбит/с | Меньше помех, меньше дальность |
| 802.11b | 2.4 ГГц | 11 Мбит/с | Первый массовый Wi-Fi |
| 802.11g | 2.4 ГГц | 54 Мбит/с | Совместим с b |
| 802.11n (Wi-Fi 4) | 2.4 + 5 ГГц | 600 Мбит/с | MIMO |
| 802.11ac (Wi-Fi 5) | 5 ГГц | ~3.5 Гбит/с | MU-MIMO, beamforming |
| 802.11ax (Wi-Fi 6) | 2.4 + 5 + 6 ГГц | ~9.6 Гбит/с | OFDMA |

### Каналы 2.4 ГГц:
Всего 11–14 каналов. **Неперекрывающиеся: 1, 6, 11** - их используют рядом стоящие AP.

### Безопасность Wi-Fi:
- WEP - устарел, легко взламывается
- WPA - улучшенный WEP (TKIP)
- **WPA2** - текущий стандарт (AES-CCMP шифрование)
- **WPA3** - новейший стандарт (SAE вместо PSK)

---

## Редкие термины - могут встретиться

| Термин | Расшифровка | Описание |
|---|---|---|
| **APIPA** | Automatic Private IP Addressing | 169.254.x.x - Windows назначает если нет DHCP |
| **SLAAC** | Stateless Address Autoconfiguration | IPv6-устройство само конфигурирует адрес без DHCP |
| **EUI-64** | Extended Unique Identifier 64-bit | Метод генерации IPv6 interface ID из MAC-адреса |
| **FHRP** | First Hop Redundancy Protocol | Класс протоколов: HSRP, VRRP, GLBP |
| **PoE** | Power over Ethernet | Питание устройств через Ethernet кабель (802.3af/at) |
| **MPLS** | Multi-Protocol Label Switching | Высокоскоростная маршрутизация по меткам (WAN) |
| **GRE** | Generic Routing Encapsulation | Туннельный протокол (IP Protocol 47) |
| **CAPWAP** | Control and Provisioning of Wireless Access Points | Протокол между WLC и AP (UDP 5246/5247) |
| **WLC** | Wireless LAN Controller | Централизованное управление точками доступа |
| **LWAP** | Lightweight Access Point | AP управляемая через WLC |
| **AAA** | Authentication, Authorization, Accounting | Трёхкомпонентная система доступа |
| **QoS** | Quality of Service | Приоритизация трафика (голос > данные) |
| **SVI** | Switch Virtual Interface | Виртуальный интерфейс коммутатора (для управления или Inter-VLAN) |
| **MIB** | Management Information Base | База данных SNMP объектов на устройстве |
| **OID** | Object Identifier | Идентификатор объекта в MIB |
| **TTL** | Time to Live | Поле в IPv4 пакете. Каждый router уменьшает на 1. При 0 - пакет отбрасывается |
| **MTU** | Maximum Transmission Unit | Максимальный размер фрейма. Ethernet стандарт = **1500 байт** |
| **BPDU** | Bridge Protocol Data Unit | Служебные фреймы STP для выбора Root Bridge |
| **LSA** | Link State Advertisement | Служебные пакеты OSPF для обмена топологией |
| **AS** | Autonomous System | Сеть под единым административным управлением (BGP использует AS номера) |
| **CIDR** | Classless Inter-Domain Routing | Бесклассовая адресация (позволяет /25, /28, etc.) |
| **VLSM** | Variable Length Subnet Mask | Разные маски для разных подсетей одной сети |

---

## Cisco IOS - важные детали

### Типы паролей
- `password` - хранится в открытом виде (plain text)
- `secret` - хранится в виде MD5-хэша (более безопасно)
- `service password-encryption` - шифрует все plain-text пароли в конфиге (тип 7, слабое)

### Файлы конфигурации
- `running-config` - текущая конфигурация в RAM (теряется при перезагрузке)
- `startup-config` - сохранённая конфигурация в NVRAM
- `copy running-config startup-config` = `write memory` = `wr`

### Boot-последовательность Cisco
1. POST (Power-On Self Test)
2. Bootstrap загружает IOS из Flash
3. IOS ищет `startup-config` в NVRAM
4. Если нет → Setup mode

### Регистр конфигурации (Config Register)
- `0x2102` - default, загружать IOS из Flash
- `0x2142` - игнорировать startup-config (для сброса пароля)

---

## Числа которые надо знать точно

| Что | Число |
|---|---|
| Бит в IPv4 адресе | 32 |
| Бит в IPv6 адресе | 128 |
| Бит в MAC-адресе | 48 |
| Октет = байт | 8 бит |
| Max VLAN ID | 4094 (4095 зарезервирован) |
| Max hops RIP | 15 (16 = недостижимо) |
| STP Hello таймер | 2 сек |
| STP Forward Delay | 15 сек |
| STP Max Age | 20 сек |
| STP полное сходство | 50 сек |
| Default MTU Ethernet | 1500 байт |
| Default STP Priority | 32768 |
| Default HSRP Priority | 100 |
| OSPF Hello (broadcast) | 10 сек |
| OSPF Dead (broadcast) | 40 сек |
| Wildcard /24 | 0.0.0.255 |
| Wildcard /16 | 0.0.255.255 |
| Wildcard /8 | 0.255.255.255 |
| Broadcast октет | 255 |
| Loopback IPv4 | 127.0.0.1 |
| APIPA диапазон | 169.254.0.0/16 |

---
  protected: true
---

#labs

# Мидтерм — Полный справочник по темам

> [!abstract] Суть
> Мидтерм похож на Lab7. Топология: несколько коммутаторов (2960), роутеры (2911), L3 коммутаторы (3650), серверы и ноутбуки. Ниже — все возможные темы: название, описание, где встречается, команды и решение.

---

## 1. Hostname настройка

**Описание:** Имя устройства — самое базовое. На мидтерме могут оставить одно устройство без hostname как troubleshooting задание.

**Где встречается:** Любое устройство — роутер, коммутатор.

**Команды:**

```
enable
configure terminal
hostname R1
end
write memory
```

`hostname R1` #ciscoIOScommand Устанавливает имя устройства. Имя отображается в приглашении командной строки.

> [!tip] Проверка
> После команды приглашение сразу меняется: `Router(config)#` → `R1(config)#`

---

## 2. VLAN — создание и назначение портов

**Описание:** Виртуальные локальные сети разделяют трафик на L2 уровне. Без VLAN весь трафик в одном broadcast домене. #networkterm

**Где встречается:** На всех коммутаторах (2960, 3650) — DSW1, DSW2, ASW1 и т.д.

### Создать VLAN и назначить имя:

```
enable
configure terminal
vlan 10
 name VLAN10
vlan 20
 name VLAN20
vlan 30
 name VLAN30
exit
```

`vlan 10` #ciscoIOScommand Создаёт VLAN с номером 10.

### Назначить access порт:

```
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
exit
```

`switchport mode access` #ciscoIOScommand Переводит порт в access режим — порт принимает трафик только одного VLAN.

`switchport access vlan 10` #ciscoIOScommand Назначает VLAN 10 на access порт.

### Настроить trunk порт:

```
interface gigabitEthernet 0/1
 switchport mode trunk
 switchport trunk native vlan 1
 switchport trunk allowed vlan 10,20,30
exit
```

`switchport mode trunk` #ciscoIOScommand Переводит порт в trunk режим — порт передаёт трафик нескольких VLAN с тегами 802.1Q.

`switchport trunk allowed vlan 10,20,30` #ciscoIOScommand Разрешает указанные VLAN проходить по trunk порту.

### Проверка:

```
show vlan brief
show interfaces trunk
```

`show vlan brief` #ciscoIOScommand Показывает все VLAN и порты назначенные к ним.

`show interfaces trunk` #ciscoIOScommand Показывает все trunk порты и разрешённые VLAN на них.

> [!warning] Ловушка
> Если порт не виден в `show vlan brief` — он или trunk, или в VLAN 1 (default). Trunk порты не показываются в этой команде.

---

## 3. Inter-VLAN Routing (Router-on-a-Stick)

**Описание:** Маршрутизация между VLAN через один физический интерфейс роутера с сабинтерфейсами. Роутер подключён к trunk порту коммутатора. #networkterm

**Где встречается:** R1 в топологии мидтерма — как в Lab7.

### На коммутаторе — trunk к роутеру:

```
interface gigabitEthernet 0/1
 switchport mode trunk
exit
```

### На роутере — сабинтерфейсы:

```
interface gigabitEthernet 0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
 no shutdown
exit

interface gigabitEthernet 0/0.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
 no shutdown
exit

interface gigabitEthernet 0/0.30
 encapsulation dot1Q 30
 ip address 10.0.30.1 255.255.255.0
 no shutdown
exit

interface gigabitEthernet 0/0
 no shutdown
exit
```

`encapsulation dot1Q 10` #ciscoIOScommand Привязывает сабинтерфейс к VLAN 10. Роутер будет обрабатывать трафик с тегом VLAN 10.

> [!important] Порядок важен
> Сначала `encapsulation dot1Q`, потом `ip address`. Также не забудь поднять главный интерфейс (`no shutdown` на `Gi0/0`).

### Проверка:

```
show ip route
ping 10.0.20.1 source 10.0.10.1
```

---

## 4. Inter-VLAN Routing на L3 коммутаторе (SVI)

**Описание:** 3650 (multilayer switch) может маршрутизировать между VLAN через SVI — Switch Virtual Interface. Альтернатива Router-on-a-Stick. #networkterm

**Где встречается:** DSW1, DSW2 (3650-24PS) в правой части топологии.

```
ip routing

interface vlan 10
 ip address 10.0.10.252 255.255.255.0
 no shutdown
exit

interface vlan 20
 ip address 10.0.20.252 255.255.255.0
 no shutdown
exit
```

`ip routing` #ciscoIOScommand Включает L3 маршрутизацию на multilayer коммутаторе. Без этой команды коммутатор не маршрутизирует.

`interface vlan 10` #ciscoIOScommand Создаёт SVI для VLAN 10. SVI — виртуальный интерфейс коммутатора, который является gateway для устройств в VLAN 10.

---

## 5. FHRP — HSRP (Hot Standby Router Protocol)

**Описание:** Протокол резервирования первого шлюза. Два L3 устройства делят виртуальный IP — одно Active, второе Standby. Если Active падает — Standby берёт на себя трафик автоматически. #abbreviation

**Где встречается:** DSW1 (Active) и DSW2 (Standby) в топологии.

### DSW1 — Active (приоритет выше):

```
interface vlan 10
 standby 1 ip 10.0.10.254
 standby 1 priority 110
 standby 1 preempt
exit

interface vlan 20
 standby 2 ip 10.0.20.254
 standby 2 priority 110
 standby 2 preempt
exit
```

### DSW2 — Standby (приоритет ниже, по умолчанию 100):

```
interface vlan 10
 standby 1 ip 10.0.10.254
exit

interface vlan 20
 standby 2 ip 10.0.20.254
exit
```

`standby 1 ip 10.0.10.254` #ciscoIOScommand Задаёт виртуальный IP адрес HSRP группы 1. Это IP который прописывается как default gateway на конечных устройствах.

`standby 1 priority 110` #ciscoIOScommand Устанавливает приоритет HSRP. Кто выше — тот Active. Default = 100.

`standby 1 preempt` #ciscoIOScommand Позволяет устройству вернуть роль Active автоматически когда оно восстановится после падения.

### Проверка:

```
show standby brief
show standby
```

`show standby brief` #ciscoIOScommand Показывает HSRP группы, роль (Active/Standby), виртуальный IP и приоритет.

> [!tip] Memory Hook
> HSRP = "горячий резерв". Виртуальный IP — один для всех, но только один маршрутизатор реально отвечает на него. Смерть Active → Standby поднимает флаг.

| Параметр | DSW1 (Active) | DSW2 (Standby) |
|---|---|---|
| Приоритет | 110 | 100 (default) |
| Роль | Active | Standby |
| Виртуальный IP | одинаковый | одинаковый |
| preempt | да | нет |

---

## 6. DHCP

**Описание:** Протокол автоматической выдачи IP адресов. Клиенты получают IP, маску, шлюз и DNS без ручной настройки. #abbreviation

**Где встречается:** R1 или отдельный сервер. Для VLAN10, VLAN20 — чтобы Laptop'ы получали IP автоматически.

### Настройка DHCP пула на роутере:

```
ip dhcp excluded-address 10.0.10.1 10.0.10.20
ip dhcp excluded-address 10.0.20.1 10.0.20.20

ip dhcp pool VLAN10
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 8.8.8.8
exit

ip dhcp pool VLAN20
 network 10.0.20.0 255.255.255.0
 default-router 10.0.20.1
 dns-server 8.8.8.8
exit
```

`ip dhcp excluded-address 10.0.10.1 10.0.10.20` #ciscoIOScommand Исключает диапазон адресов из выдачи DHCP. Обычно резервируют первые адреса для роутеров, коммутаторов.

`ip dhcp pool VLAN10` #ciscoIOScommand Создаёт DHCP пул с именем VLAN10.

`network 10.0.10.0 255.255.255.0` #ciscoIOScommand Задаёт сеть из которой будут выдаваться адреса.

`default-router 10.0.10.1` #ciscoIOScommand Задаёт шлюз по умолчанию который получат клиенты.

### Если DHCP сервер на отдельном устройстве — DHCP Relay:

```
interface gigabitEthernet 0/0.10
 ip helper-address 10.0.99.100
exit
```

`ip helper-address 10.0.99.100` #ciscoIOScommand Пересылает DHCP broadcast запросы клиентов на указанный DHCP сервер. Используется когда сервер в другой подсети.

### Проверка:

```
show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
```

`show ip dhcp binding` #ciscoIOScommand Показывает какие IP адреса выданы и каким MAC адресам.

> [!warning] Ловушка
> Если клиент не получает IP — проверь `ip helper-address` на интерфейсе роутера который смотрит в VLAN клиента.

---

## 7. Port Security

**Описание:** Функция коммутатора ограничивающая доступ к порту по MAC адресу. Если подключается неизвестное устройство — порт уходит в err-disabled. #networkterm

**Где встречается:** Access порты коммутаторов к серверам и ноутбукам. Классика Lab7.

### Static MAC (MAC известен):

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

### Sticky MAC (MAC неизвестен):

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

`switchport port-security` #ciscoIOScommand Включает Port Security на порту.

`switchport port-security maximum 2` #ciscoIOScommand Максимум 2 MAC адреса на порту.

`switchport port-security mac-address sticky` #ciscoIOScommand Коммутатор сам запомнит MAC первого подключённого устройства.

### Найти MAC нарушителя:

```
show port-security
show port-security interface fastEthernet 0/1
show mac address-table
```

`show port-security` #ciscoIOScommand Показывает статус Port Security, **Last Source Address** — последний MAC который пытался подключиться.

| Ситуация | Метод |
|---|---|
| MAC **известен** (виден в логах) | Static: `mac-address XXXX.XXXX.XXXX` |
| MAC **неизвестен** (сервер недоступен) | Sticky: `mac-address sticky` |

> [!danger] Порядок команд
> Всегда: `maximum 2` → потом `mac-address`. Иначе ошибка "maximum limit reached".

> [!warning] err-disabled = оранжевый порт в Packet Tracer
> Исправление: сначала перенастрой port-security, потом `shutdown` → `no shutdown`.

---

## 8. SSH и Telnet — удалённый доступ

**Описание:** Протоколы удалённого управления устройствами. Telnet — без шифрования. SSH — зашифрованный. #networkterm

**Где встречается:** На всех устройствах для management доступа.

### Telnet:

```
line vty 0 4
 password cisco
 login
 transport input telnet
exit
```

### SSH (более безопасный):

```
ip domain-name cisco.com
crypto key generate rsa modulus 1024
ip ssh version 2

username admin privilege 15 secret cisco

line vty 0 4
 login local
 transport input ssh
exit
```

`crypto key generate rsa modulus 1024` #ciscoIOScommand Генерирует RSA ключи для SSH. Минимум 768 бит, рекомендуется 1024+.

`ip ssh version 2` #ciscoIOScommand Принудительно использует SSH версию 2 (более безопасную).

`login local` #ciscoIOScommand Требует аутентификацию через локальную базу пользователей (username/password).

### Подключение:

```
telnet 10.0.1.10
ssh -l admin 10.0.1.10
```

### Проверка:

```
show ip ssh
show users
```

---

## 9. Static Routes — статические маршруты

**Описание:** Маршруты прописанные вручную. Роутер знает куда отправлять трафик для конкретной сети. #networkterm

**Где встречается:** Когда нет OSPF — нужно вручную указать пути между сетями.

```
ip route 10.0.20.0 255.255.255.0 10.0.12.2
ip route 0.0.0.0 0.0.0.0 192.168.1.1
```

`ip route 10.0.20.0 255.255.255.0 10.0.12.2` #ciscoIOScommand Статический маршрут: трафик до сети 10.0.20.0/24 отправлять через next-hop 10.0.12.2.

`ip route 0.0.0.0 0.0.0.0 192.168.1.1` #ciscoIOScommand Default route — весь трафик без конкретного маршрута отправлять на 192.168.1.1 (шлюз провайдера).

### Проверка:

```
show ip route
ping 10.0.20.1
traceroute 10.0.20.1
```

`show ip route` #ciscoIOScommand Показывает таблицу маршрутизации. S = static, C = connected, O = OSPF, R = RIP.

---

## 10. OSPF

**Описание:** Динамический протокол маршрутизации. Роутеры обмениваются информацией о сетях автоматически. #abbreviation

**Где встречается:** Между роутерами в топологии — R1, R2, R3, R4.

```
router ospf 1
 router-id 1.1.1.1
 network 10.0.10.0 0.0.0.255 area 0
 network 10.0.12.0 0.0.0.255 area 0
 default-information originate
exit
```

`router ospf 1` #ciscoIOScommand Запускает процесс OSPF с ID 1.

`router-id 1.1.1.1` #ciscoIOScommand Задаёт уникальный идентификатор роутера в OSPF. Обычно используют loopback адрес.

`network 10.0.10.0 0.0.0.255 area 0` #ciscoIOScommand Включает интерфейсы в сети 10.0.10.0/24 в OSPF area 0. Wildcard = инверсия маски.

`default-information originate` #ciscoIOScommand Распространяет default route через OSPF на всех соседей.

### Проверка:

```
show ip ospf neighbor
show ip ospf interface
show ip route ospf
```

`show ip ospf neighbor` #ciscoIOScommand Показывает OSPF соседей и их состояние. FULL = нормально.

> [!tip] Wildcard маска
> /24 → wildcard 0.0.0.255 | /30 → wildcard 0.0.0.3 | /16 → wildcard 0.255.255.255

---

## 11. IPv4 Subnetting

**Описание:** Разбивка сети на подсети. Могут дать блок адресов и попросить распределить по VLAN/сегментам.

**Где встречается:** Теория + назначение IP в топологии.

| Маска | CIDR | Хостов | Пример |
|---|---|---|---|
| 255.255.255.0 | /24 | 254 | 10.0.10.0/24 |
| 255.255.255.128 | /25 | 126 | 10.0.10.0/25 |
| 255.255.255.192 | /26 | 62 | 10.0.10.0/26 |
| 255.255.255.224 | /27 | 30 | 10.0.10.0/27 |
| 255.255.255.240 | /28 | 14 | 10.0.10.0/28 |
| 255.255.255.252 | /30 | 2 | 10.0.12.0/30 |

> [!tip] Формула
> Хостов = 2^(32-prefix) - 2. Например /26: 2^6 - 2 = 62 хоста.

### Назначение IP на интерфейс:

```
interface gigabitEthernet 0/0
 ip address 10.0.10.1 255.255.255.0
 no shutdown
exit
```

`ip address 10.0.10.1 255.255.255.0` #ciscoIOScommand Назначает IPv4 адрес и маску на интерфейс.

`no shutdown` #ciscoIOScommand Включает интерфейс. По умолчанию интерфейсы роутера выключены (administratively down).

---

## 12. IPv6 — Dual Stack

**Описание:** Параллельная работа IPv4 и IPv6 на одном интерфейсе. IPv6 адрес записывается в шестнадцатеричном формате через двоеточия. #networkterm

**Где встречается:** На интерфейсах роутеров параллельно с IPv4.

```
ipv6 unicast-routing

interface gigabitEthernet 0/0.10
 ipv6 address 2001:DB8:10::1/64
 ipv6 enable
exit
```

`ipv6 unicast-routing` #ciscoIOScommand Включает IPv6 маршрутизацию на роутере. Без этого роутер не форвардит IPv6 трафик.

`ipv6 address 2001:DB8:10::1/64` #ciscoIOScommand Назначает статический IPv6 адрес на интерфейс.

`ipv6 enable` #ciscoIOScommand Включает IPv6 на интерфейсе и генерирует link-local адрес (fe80::).

### IPv6 Static Route:

```
ipv6 route 2001:DB8:20::/64 2001:DB8:12::2
ipv6 route ::/0 2001:DB8:ISP::1
```

`ipv6 route ::/0 2001:DB8:ISP::1` #ciscoIOScommand IPv6 default route — аналог `ip route 0.0.0.0 0.0.0.0`.

### Проверка:

```
show ipv6 interface brief
show ipv6 route
ping ipv6 2001:DB8:20::1
```

`show ipv6 interface brief` #ciscoIOScommand Показывает IPv6 адреса на всех интерфейсах.

| Тип адреса | Пример | Описание |
|---|---|---|
| Global Unicast | 2001:DB8::/32 | Публичный IPv6 |
| Link-Local | fe80::/10 | Только в пределах сегмента |
| Loopback | ::1/128 | Аналог 127.0.0.1 |
| Multicast | ff02::/16 | Групповая рассылка |

---

## 13. ACL — Access Control List

**Описание:** Список правил для фильтрации трафика на роутере. Разрешает или запрещает пакеты по IP, протоколу, порту. #abbreviation

**Где встречается:** На интерфейсах роутеров — фильтрация между VLAN или к серверам.

### Standard ACL (только по source IP):

```
ip access-list standard BLOCK_VLAN10
 deny 10.0.10.0 0.0.0.255
 permit any
exit

interface gigabitEthernet 0/0.20
 ip access-group BLOCK_VLAN10 in
exit
```

### Extended ACL (по source, destination, протоколу, порту):

```
ip access-list extended ALLOW_WEB
 permit tcp 10.0.10.0 0.0.0.255 any eq 80
 permit tcp 10.0.10.0 0.0.0.255 any eq 443
 deny ip any any
exit

interface gigabitEthernet 0/0
 ip access-group ALLOW_WEB in
exit
```

`ip access-group ALLOW_WEB in` #ciscoIOScommand Применяет ACL к интерфейсу. `in` = фильтрует входящий трафик, `out` = исходящий.

### Проверка:

```
show ip access-lists
show ip interface gigabitEthernet 0/0
```

> [!warning] Неявное deny
> В конце каждого ACL есть неявное `deny any` — весь трафик не попавший под правила будет заблокирован. Всегда добавляй `permit any` если нужно пропустить остальное.

> [!tip] Размещение ACL
> Standard ACL — ближе к destination. Extended ACL — ближе к source.

---

## 14. NAT — Network Address Translation

**Описание:** Преобразование приватных IP адресов в публичные для выхода в интернет. #abbreviation

**Где встречается:** На граничном роутере (R1 или R3) — между LAN и ISP.

```
ip nat inside source list 1 interface gigabitEthernet 0/1 overload

access-list 1 permit 10.0.0.0 0.255.255.255

interface gigabitEthernet 0/0
 ip nat inside
exit

interface gigabitEthernet 0/1
 ip nat outside
exit
```

`ip nat inside source list 1 interface Gi0/1 overload` #ciscoIOScommand PAT (Port Address Translation) — все внутренние адреса маскируются под один внешний IP интерфейса. `overload` = PAT.

`ip nat inside` #ciscoIOScommand Помечает интерфейс как "внутренний" (LAN сторона).

`ip nat outside` #ciscoIOScommand Помечает интерфейс как "внешний" (WAN/ISP сторона).

### Проверка:

```
show ip nat translations
show ip nat statistics
```

---

## 15. STP — Spanning Tree Protocol

**Описание:** Протокол предотвращающий петли на L2 уровне при избыточных соединениях между коммутаторами. Блокирует избыточные порты. #abbreviation

**Где встречается:** Между DSW1, DSW2 и access коммутаторами. Красные линии на топологии — возможно заблокированные STP порты.

```
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary

spanning-tree mode rapid-pvst
```

`spanning-tree vlan 10 root primary` #ciscoIOScommand Делает коммутатор Root Bridge для VLAN 10. Устанавливает приоритет 24576.

`spanning-tree mode rapid-pvst` #ciscoIOScommand Включает Rapid PVST+ — более быстрая версия STP, отдельный экземпляр на каждый VLAN.

### Проверка:

```
show spanning-tree
show spanning-tree vlan 10
```

`show spanning-tree` #ciscoIOScommand Показывает STP топологию: Root Bridge, роли портов (Root/Designated/Alternate), состояния.

| Роль порта | Описание |
|---|---|
| Root Port | Порт ближайший к Root Bridge |
| Designated Port | Лучший порт на сегменте |
| Alternate/Blocked | Заблокирован для предотвращения петли |

---

## 16. EtherChannel (LACP/PAGP)

**Описание:** Объединение нескольких физических каналов в один логический для увеличения пропускной способности и резервирования. #networkterm

**Где встречается:** Между DSW1 и DSW2 — часто делают EtherChannel на uplink линках.

```
interface range gigabitEthernet 0/1 - 2
 channel-group 1 mode active
exit

interface port-channel 1
 switchport mode trunk
exit
```

`channel-group 1 mode active` #ciscoIOScommand Добавляет интерфейсы в EtherChannel группу 1 в режиме LACP active.

| Протокол | Режимы |
|---|---|
| LACP (802.3ad) | active / passive |
| PAgP (Cisco) | desirable / auto |

### Проверка:

```
show etherchannel summary
show interfaces port-channel 1
```

---

## 17. ICMP и Диагностика

**Описание:** ICMP используется для проверки связи (ping) и трассировки пути (traceroute). #abbreviation

**Где встречается:** Проверка после любой настройки.

```
ping 10.0.20.1
ping 10.0.20.1 source 10.0.10.1
traceroute 10.0.20.1

ping ipv6 2001:DB8:20::1
```

`ping 10.0.20.1` #ciscoIOScommand Проверяет связь с устройством через ICMP Echo Request. `!` = успех, `.` = таймаут, `U` = unreachable.

`ping 10.0.20.1 source 10.0.10.1` #ciscoIOScommand Ping с указанием source IP — имитирует трафик из VLAN 10 в VLAN 20.

`traceroute 10.0.20.1` #ciscoIOScommand Показывает путь пакета через все промежуточные роутеры до цели.

| Символ ping | Значение |
|---|---|
| `!` | Успешный ответ |
| `.` | Таймаут (нет ответа) |
| `U` | Destination Unreachable |
| `N` | Network Unreachable |

---

## 18. Loopback интерфейс

**Описание:** Виртуальный интерфейс роутера который всегда UP. Используется как Router-ID для OSPF и для управления. #networkterm

**Где встречается:** На роутерах — для OSPF router-id.

```
interface loopback 0
 ip address 1.1.1.1 255.255.255.255
 no shutdown
exit
```

`interface loopback 0` #ciscoIOScommand Создаёт loopback интерфейс. Всегда в состоянии UP/UP — не зависит от физических соединений.

> [!tip] /32 маска на loopback
> Обычно используют /32 (255.255.255.255) — это host route, один адрес только для этого роутера.

---

## 19. Transport Layer — теория

**Описание:** L4 модели OSI. TCP и UDP — два основных транспортных протокола.

| Параметр | TCP | UDP |
|---|---|---|
| Соединение | Connection-oriented | Connectionless |
| Надёжность | Да (ACK, retransmit) | Нет |
| Скорость | Медленнее | Быстрее |
| Примеры | HTTP, FTP, SSH, Telnet | DNS, DHCP, TFTP, VoIP |
| Handshake | 3-way (SYN-SYN/ACK-ACK) | Нет |

**Известные порты:**

| Порт | Протокол |
|---|---|
| 20/21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 67/68 | DHCP |
| 80 | HTTP |
| 443 | HTTPS |
| 161 | SNMP |

> [!note] На мидтерме
> Теория TCP/UDP — скорее вопрос, не настройка в Packet Tracer. Запомни: TCP = надёжно, UDP = быстро.

---

## 20. Общий Troubleshooting Checklist

> [!important] Последовательность проверки
> Всегда иди от L1 → L2 → L3. Физика → Линк → Маршрутизация.

```
show interfaces status
show ip interface brief
show ip route
show vlan brief
show interfaces trunk
show port-security
show spanning-tree
show standby brief
show ip ospf neighbor
```

`show ip interface brief` #ciscoIOScommand Краткий статус всех интерфейсов — IP, статус (up/down), протокол.

### Частые проблемы и решения:

| Проблема | Возможная причина | Решение |
|---|---|---|
| Порт оранжевый | err-disabled (Port Security) | Перенастроить, `shutdown` → `no shutdown` |
| Нет ping между VLAN | Нет Inter-VLAN routing | Проверить сабинтерфейсы / SVI / `ip routing` |
| OSPF сосед не появляется | Разные area, сеть не добавлена | Проверить `network` команды в OSPF |
| Клиент не получает DHCP | Нет `ip helper-address` | Добавить `ip helper-address` на интерфейс |
| HSRP не работает | Разные group номера | Убедиться что group одинаковая на обоих |
| trunk не пропускает VLAN | `allowed vlan` не настроен | `switchport trunk allowed vlan add X` |

> [!success] Итог
> Если понял этот файл — можешь настроить полную топологию мидтерма: VLAN → Inter-VLAN → HSRP → DHCP → Port Security → статические маршруты → проверка ping.

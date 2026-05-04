---
  protected: true
---

#labs

# Мидтерм — Все команды из книг

> [!abstract] Источник
> **Только команды из Book 1 и Book 2** которые ты реально прошёл. Темы без источника в книгах (NAT, ACL, BGP, EIGRP, RIP) — не включены. Каждая команда: синтаксис, объяснение из книги, где применяется в топологии.

> [!warning] Предупреждение по прошлым файлам
> Midterm Prep.md и Protocols Reference.md содержали темы **не из твоих книг** (NAT, ACL, OSPF полная настройка, BGP, EIGRP). На мидтерме их не будет — не учи лишнее.

---

## Блок 1 — Базовая настройка (Book 2, Module 1)

**Источник:** 1.1, 1.4 — Configure a Switch/Router with Initial Settings

---

### Начальная настройка любого устройства

```
enable
configure terminal
hostname R1
enable secret class
line console 0
 password cisco
 login
 exit
line vty 0 4
 password cisco
 login
 exit
service password-encryption
banner motd $ Authorized Access Only! $
end
copy running-config startup-config
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `enable` | Войти в privileged EXEC mode | Любое устройство |
| `configure terminal` | Войти в global config mode | Любое устройство |
| `hostname R1` | Задать имя устройства. Prompt сразу меняется. | Все: R1, R2, ASW1, DSW1... |
| `enable secret class` | Пароль для входа в enable. `secret` = MD5, безопаснее чем `password` | Все устройства |
| `line console 0` | Настройка физической консоли | Все устройства |
| `password cisco` | Пароль на line (console или vty) | Все устройства |
| `login` | Включить проверку пароля на line | Все устройства |
| `line vty 0 4` | Настройка виртуальных линий для Telnet/SSH | Все устройства |
| `service password-encryption` | Зашифровать все plain-text пароли в конфиге | Все устройства |
| `banner motd $ текст $` | Предупреждение при входе на устройство | Все устройства |
| `end` | Выйти из config mode в privileged EXEC | Любой уровень config |
| `copy running-config startup-config` | Сохранить конфиг. Без этого после reload всё сотрётся | Все устройства |
| `write memory` | Сокращённый alias для `copy run start` | Все устройства |

> [!tip] Пароли на мидтерме
> Стандарт в лабах: `enable secret class`, `password cisco`.
> Препод сказал: пароль может быть именем протокола — пробуй `ospf`, `hsrp`, `vlan`, `telnet`, `dhcp`, `cisco`, `class`.

---

### Настройка интерфейса роутера (Book 2, Module 1.4)

```
interface gigabitEthernet 0/0
 ip address 10.0.10.1 255.255.255.0
 ipv6 address 2001:db8:acad:1::1/64
 description Link to LAN
 no shutdown
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `interface gigabitEthernet 0/0` | Войти в настройку физического интерфейса | R1, R2, R3 |
| `ip address 10.0.10.1 255.255.255.0` | Назначить IPv4 адрес и маску | R1, R2, R3 — все физические интерфейсы |
| `ipv6 address 2001:db8:acad:1::1/64` | Назначить IPv6 GUA адрес | R1, R2, R3 если dual-stack |
| `description Link to LAN` | Текстовая подпись интерфейса — только для чтения конфига | Любой интерфейс |
| `no shutdown` | **Включить** интерфейс. По умолчанию роутерные порты выключены | Все интерфейсы роутера |
| `shutdown` | Выключить интерфейс | Для отключения или Port Security recovery |

---

### SVI — Management IP на коммутаторе (Book 2, Module 1.1)

```
interface vlan 99
 ip address 172.17.99.11 255.255.255.0
 no shutdown
exit
ip default-gateway 172.17.99.1
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `interface vlan 99` | Создать SVI для management VLAN | ASW1, ASW2, ASW3 — L2 коммутаторы |
| `ip address 172.17.99.11 255.255.255.0` | Management IP коммутатора | L2 коммутаторы |
| `ip default-gateway 172.17.99.1` | Шлюз для management доступа из другой сети | L2 коммутаторы (не L3!) |

> [!warning] SVI не поднимется если VLAN не существует или в нём нет активного порта

---

## Блок 2 — Настройка портов коммутатора (Book 2, Module 1.2)

**Источник:** 1.2 — Configure Switch Ports

```
interface fastEthernet 0/1
 duplex full
 speed 100
 mdix auto
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `duplex full` | Полный дуплекс — одновременная передача в обе стороны | Access порты |
| `speed 100` | Скорость 100 Мбит/с | Access порты |
| `mdix auto` | Автоопределение типа кабеля (прямой/перекрёстный) | Любой медный порт |
| `duplex auto` | Автосогласование дуплекса | По умолчанию |
| `speed auto` | Автосогласование скорости | По умолчанию |
| `interface range fa0/1 - 24` | Настроить диапазон интерфейсов одновременно | Отключение unused портов |

---

## Блок 3 — SSH (Book 2, Module 1.3)

**Источник:** 1.3 — Secure Remote Access

```
ip domain-name cisco.com
crypto key generate rsa
 1024
username admin secret ccna
line vty 0 15
 transport input ssh
 login local
 exit
ip ssh version 2
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `ip domain-name cisco.com` | Домен нужен для генерации RSA ключей | Любое устройство где нужен SSH |
| `crypto key generate rsa` | Сгенерировать RSA ключи. Вводи `1024` когда спросит | Любое устройство |
| `username admin secret ccna` | Создать локального пользователя для `login local` | Любое устройство |
| `transport input ssh` | Разрешить только SSH на VTY линиях (заблокирует Telnet) | Все устройства с SSH |
| `transport input telnet` | Разрешить только Telnet | Если SSH не нужен |
| `transport input telnet ssh` | Разрешить и Telnet и SSH | Смешанный доступ |
| `login local` | Аутентификация через локальную БД пользователей | Вместо просто `login` |
| `ip ssh version 2` | Использовать SSH v2 (безопаснее v1) | Обязательно после keygen |
| `show ip ssh` | Показать статус SSH — включён, версия | Проверка |
| `show ssh` | Активные SSH сессии | Проверка |

> [!important] Порядок SSH: `domain-name` → `crypto key generate rsa` → `username` → `vty transport input ssh login local` → `ip ssh version 2`

---

## Блок 4 — VLAN (Book 2, Module 3)

**Источник:** 3.3 — VLAN Configuration, 3.4 — VLAN Trunks

---

### Создание VLAN

```
vlan 10
 name VLAN10
vlan 20
 name VLAN20
vlan 30
 name VLAN30
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `vlan 10` | Создать VLAN с ID 10 | Все коммутаторы |
| `name VLAN10` | Дать VLAN понятное имя | Все коммутаторы |
| `no vlan 20` | Удалить VLAN из базы | Если нужно убрать |
| `delete flash:vlan.dat` | Полностью стереть VLAN базу | Factory reset коммутатора |

---

### Access порт (порт к конечному устройству)

```
interface fastEthernet 0/1
 switchport mode access
 switchport access vlan 10
 no shutdown
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `switchport mode access` | Порт принимает трафик только одного VLAN. Обязателен перед `port-security` | ASW1/ASW2/ASW3 — порты к ноутбукам и серверам |
| `switchport access vlan 10` | Назначить VLAN 10 на этот access порт | ASW1/ASW2 — порты к Laptop |
| `no switchport access vlan` | Убрать назначение, вернуть в VLAN 1 | Если ошиблись |
| `switchport voice vlan 150` | Назначить voice VLAN (для IP телефонов) | Если есть VoIP |

---

### Trunk порт (порт между коммутаторами или к роутеру)

```
interface gigabitEthernet 0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `switchport mode trunk` | Порт передаёт трафик нескольких VLAN с 802.1Q тегами | ASW → R1 (Router-on-a-Stick), ASW → DSW |
| `switchport trunk native vlan 99` | Трафик native VLAN идёт без тега. На обоих концах должен совпадать | Trunk порты |
| `switchport trunk allowed vlan 10,20,30` | Только эти VLAN проходят по trunk | Trunk порты |
| `switchport trunk allowed vlan add 40` | Добавить VLAN к существующему списку (не заменить!) | Trunk порты |
| `no switchport trunk allowed vlan` | Убрать ограничения — разрешить все VLAN | Сброс |
| `no switchport trunk native vlan` | Вернуть native VLAN к default (VLAN 1) | Сброс |

---

### Проверка VLAN

```
show vlan brief
show vlan summary
show interfaces fa0/1 switchport
show interfaces trunk
```

| Команда | Объяснение |
|---|---|
| `show vlan brief` | Все VLAN и назначенные access порты. Trunk порты здесь **не** показываются |
| `show vlan summary` | Сколько VLAN всего |
| `show interfaces fa0/1 switchport` | Режим порта (access/trunk), native VLAN, allowed VLANs |
| `show interfaces trunk` | Все trunk порты и разрешённые VLAN на них |

> [!warning] `switchport trunk allowed vlan 30` заменяет весь список! Используй `add` чтобы не потерять остальные VLAN

---

## Блок 5 — Inter-VLAN Routing (Book 2, Module 4)

**Источник:** 4.2 — Router-on-a-Stick, 4.3 — Layer 3 Switch

---

### Router-on-a-Stick (R1 — сабинтерфейсы)

```
interface gigabitEthernet 0/0.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
 description Default Gateway for VLAN 10
exit

interface gigabitEthernet 0/0.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
exit

interface gigabitEthernet 0/0.99
 encapsulation dot1Q 99 native
 ip address 10.0.99.1 255.255.255.0
exit

interface gigabitEthernet 0/0
 no shutdown
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `interface gigabitEthernet 0/0.10` | Создать сабинтерфейс `.10` на физическом `Gi0/0` | R1 — для каждого VLAN |
| `encapsulation dot1Q 10` | Привязать сабинтерфейс к VLAN 10 по 802.1Q | Каждый сабинтерфейс |
| `encapsulation dot1Q 99 native` | Native VLAN — трафик идёт без тега | Только для native VLAN |
| `ip address 10.0.10.1 255.255.255.0` | IP = default gateway для всех устройств в VLAN 10 | Каждый сабинтерфейс |

> [!danger] Если физический `Gi0/0` выключен — все сабинтерфейсы тоже не работают. Всегда делай `no shutdown` на физическом интерфейсе.

> [!important] Порядок: `encapsulation dot1Q` → потом `ip address`

---

### L3 коммутатор — SVI routing (DSW1, DSW2)

```
ip routing

interface vlan 10
 description Default Gateway SVI for VLAN 10
 ip address 10.0.10.252 255.255.255.0
 no shutdown
exit

interface vlan 20
 ip address 10.0.20.252 255.255.255.0
 no shutdown
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `ip routing` | **Включить маршрутизацию на L3 коммутаторе.** Без этого SVI есть, но маршрутизации нет | DSW1, DSW2 (3650) |
| `interface vlan 10` | Создать SVI для VLAN 10 — это и будет gateway | DSW1, DSW2 |
| `no switchport` | Превратить L2 порт в routed порт (как на роутере) | DSW uplink к R3 |

> [!danger] Самая частая ошибка на 3650 — забыть `ip routing`. Без неё коммутатор не маршрутизирует.

---

### Проверка Inter-VLAN

```
show ip route
show ip interface brief
show interfaces gi0/0.10
show interfaces trunk
```

---

## Блок 6 — DHCP (Book 2, Module 7)

**Источник:** 7.2 — Configure a Cisco IOS DHCPv4 Server

---

### DHCPv4 сервер на роутере

```
ip dhcp excluded-address 10.0.10.1 10.0.10.20
ip dhcp excluded-address 10.0.20.1 10.0.20.20

ip dhcp pool VLAN10
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 8.8.8.8
 domain-name example.com
exit

ip dhcp pool VLAN20
 network 10.0.20.0 255.255.255.0
 default-router 10.0.20.1
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `ip dhcp excluded-address 10.0.10.1 10.0.10.20` | Исключить диапазон из выдачи — для шлюзов и серверов | R1 global config |
| `ip dhcp excluded-address 10.0.10.254` | Исключить один адрес | R1 global config |
| `ip dhcp pool VLAN10` | Создать пул с именем. Войти в dhcp-config режим | R1 — для каждого VLAN |
| `network 10.0.10.0 255.255.255.0` | Подсеть из которой выдавать адреса | В каждом пуле |
| `default-router 10.0.10.1` | Шлюз который получат клиенты | В каждом пуле |
| `dns-server 8.8.8.8` | DNS сервер для клиентов | В пуле (если нужен) |
| `domain-name example.com` | Домен для клиентов | В пуле (если нужен) |
| `lease 7` | Время аренды адреса в днях (default = 1 день) | В пуле |
| `no service dhcp` | Выключить DHCP сервис | Если нужно отключить |
| `service dhcp` | Включить DHCP сервис обратно | — |

---

### DHCP Relay Agent

```
interface gigabitEthernet 0/0.10
 ip helper-address 10.0.99.100
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `ip helper-address 10.0.99.100` | Пересылать DHCP broadcast от клиентов на сервер 10.0.99.100 | R1 — на интерфейсе смотрящем в VLAN клиентов |

> [!danger] Если DHCP сервер в другой подсети и нет `ip helper-address` — клиент адрес не получит. Это классическая ловушка.

---

### Проверка DHCP

```
show running-config | section dhcp
show ip dhcp binding
show ip dhcp server statistics
show ip interface gi0/0.10
```

| Команда | Объяснение |
|---|---|
| `show ip dhcp binding` | Какие IP выданы и каким MAC адресам |
| `show ip dhcp server statistics` | Счётчики сообщений DHCP |
| `show running-config | section dhcp` | Только DHCP конфиг |
| `show ip interface gi0/0.10` | Проверить helper-address — ищи строку `Helper address is...` |

---

## Блок 7 — HSRP (Book 2, Module 9)

**Источник:** 9.2 — HSRP

---

### DSW1 — Active (высокий приоритет)

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

### DSW2 — Standby (приоритет по умолчанию = 100)

```
interface vlan 10
 standby 1 ip 10.0.10.254
exit

interface vlan 20
 standby 2 ip 10.0.20.254
exit
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `standby 1 ip 10.0.10.254` | Виртуальный IP для HSRP группы 1. Именно этот IP прописывается как gateway на ноутбуках | DSW1 и DSW2 — одинаковый |
| `standby 1 priority 110` | Приоритет. Кто выше — тот Active. Default = 100. Если равный — побеждает больший IP | DSW1 (Active) |
| `standby 1 preempt` | Вернуть роль Active автоматически после восстановления | DSW1 |

> [!warning] Exam trap: higher priority сам по себе не возвращает Active роль после падения. Нужен `preempt`.

**Состояния HSRP:** Initial → Learn → Listen → Speak → **Standby** / **Active**

**Таймеры:** Hello = 3 сек, Hold = 10 сек

---

### Проверка HSRP

```
show standby
show standby brief
```

| Команда | Объяснение |
|---|---|
| `show standby brief` | Кратко: группа, роль (Active/Standby), Virtual IP, приоритет |
| `show standby` | Полная информация: таймеры, Virtual MAC, состояния |

---

## Блок 8 — Port Security (Book 2, Module 11)

**Источник:** 11.1 — Implement Port Security

---

### Включение Port Security

```
interface fastEthernet 0/1
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address sticky
exit
write memory
```

Или со static MAC:

```
interface fastEthernet 0/2
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address 00E0.8F8B.A56C
exit
write memory
```

| Команда | Объяснение | Где в топологии |
|---|---|---|
| `switchport mode access` | **Обязателен** перед port-security. На dynamic порту не работает | Все access порты |
| `switchport port-security` | Включить Port Security | После `mode access` |
| `switchport port-security maximum 2` | Максимум 2 MAC адреса. Default = 1. Ставь **до** `mac-address` | Перед mac-address командой |
| `switchport port-security mac-address sticky` | Коммутатор сам запомнит MAC первого подключившегося | Когда MAC неизвестен |
| `switchport port-security mac-address 00E0.8F.A56C` | Статически прописать разрешённый MAC | Когда MAC известен из `show port-security` |
| `switchport port-security violation restrict` | Нарушение: дропать + логировать + считать. Порт не выключать | Вместо default shutdown |
| `switchport port-security violation protect` | Нарушение: тихо дропать. Без лога, без счётчика | Тихая защита |
| `switchport port-security violation shutdown` | Нарушение: порт уходит в err-disabled. Default поведение | По умолчанию |
| `switchport port-security aging time 10` | Aging timer в минутах | Опционально |
| `interface range fa0/8 - 24` → `shutdown` | Отключить все неиспользуемые порты | Best practice |

**Таблица violation режимов:**

| Mode | Дропает | Syslog | Счётчик | Shutdown порта |
|---|---|---|---|---|
| `protect` | Да | Нет | Нет | Нет |
| `restrict` | Да | Да | Да | Нет |
| `shutdown` | Да | Да | Да | **Да** (err-disabled) |

> [!danger] Порядок команд: `maximum` → потом `mac-address`. Наоборот = ошибка "maximum limit reached"

---

### Восстановление err-disabled порта

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

---

### Проверка Port Security

```
show port-security
show port-security interface fa0/1
show port-security address
show run | begin interface FastEthernet0/1
```

| Команда | Объяснение |
|---|---|
| `show port-security` | Сводка по всем портам. **Last Source Address** — MAC который пытался подключиться |
| `show port-security interface fa0/1` | Детали порта: статус, максимум, нарушения |
| `show port-security address` | Таблица secure MAC адресов |
| `show interface fa0/1` | Увидеть статус `err-disabled` |

---

## Блок 9 — Static Routes (Book 2, Module 15)

**Источник:** 15.2, 15.3 — Configure IP Static Routes, Default Routes

---

### IPv4 Static Routes

```
ip route 10.0.20.0 255.255.255.0 10.0.12.2
ip route 10.0.20.0 255.255.255.0 serial 0/0/0
ip route 10.0.20.0 255.255.255.0 serial 0/0/0 10.0.12.2
ip route 0.0.0.0 0.0.0.0 192.168.1.1
```

| Команда | Тип | Объяснение | Где |
|---|---|---|---|
| `ip route 10.0.20.0 255.255.255.0 10.0.12.2` | Next-hop | До сети 10.0.20.0/24 идти через 10.0.12.2 | R1, R2, R3 |
| `ip route 10.0.20.0 255.255.255.0 s0/0/0` | Directly connected | Выходить через интерфейс Serial0/0/0 | Point-to-point |
| `ip route 10.0.20.0 255.255.255.0 s0/0/0 10.0.12.2` | Fully specified | Интерфейс + next-hop вместе | Ethernet links |
| `ip route 0.0.0.0 0.0.0.0 192.168.1.1` | Default route | Всё без конкретного маршрута — отправлять на 192.168.1.1 | Edge роутер к ISP |

---

### IPv6 Static Routes

```
ipv6 unicast-routing
ipv6 route 2001:db8:acad:1::/64 2001:db8:acad:2::2
ipv6 route ::/0 2001:db8:acad:2::2
```

| Команда | Объяснение | Где |
|---|---|---|
| `ipv6 unicast-routing` | **Включить IPv6 маршрутизацию**. Без этого роутер не форвардит IPv6 | R1, R2, R3 в global config |
| `ipv6 route 2001:db8::/64 next-hop` | IPv6 static route через next-hop | Между роутерами |
| `ipv6 route ::/0 next-hop` | IPv6 default route (аналог 0.0.0.0/0) | Edge роутер |

---

### Проверка маршрутов

```
show ip route
show ip route static
show ipv6 route
show ipv6 route static
```

| Команда | Объяснение |
|---|---|
| `show ip route` | Вся таблица маршрутизации. C=connected, L=local, S=static |
| `show ip route static` | Только статические маршруты |
| `show ipv6 route` | IPv6 таблица маршрутизации |

**Коды в routing table:**

| Код | Значение |
|---|---|
| `C` | Connected (прямое подключение) |
| `L` | Local (собственный адрес интерфейса) |
| `S` | Static (статический маршрут) |
| `S*` | Static default route |
| `O` | OSPF |

---

## Блок 10 — IPv6 адресация (Book 1, Module 12)

**Источник:** 12.4 — GUA and LLA Static Configuration

```
ipv6 unicast-routing

interface gigabitEthernet 0/0
 ipv6 address 2001:db8:acad:1::1/64
 ipv6 address fe80::1:1 link-local
 no shutdown
exit
```

| Команда | Объяснение | Где |
|---|---|---|
| `ipv6 address 2001:db8:acad:1::1/64` | GUA (Global Unicast Address) — публичный IPv6. Нет пробела между адресом и /64 | Все интерфейсы роутера |
| `ipv6 address fe80::1:1 link-local` | LLA (Link-Local Address) — читаемый вручную. Ключевое слово `link-local` обязательно | Все интерфейсы |

**Типы IPv6 адресов:**

| Тип | Диапазон | Описание |
|---|---|---|
| GUA | `2000::/3` | Глобальный, маршрутизируется в интернете |
| LLA | `fe80::/10` | Только в пределах канала, не маршрутизируется |
| Loopback | `::1/128` | Как 127.0.0.1 в IPv4 |
| Multicast | `ff00::/8` | Групповые адреса |

---

## Блок 11 — EtherChannel (Book 2, Module 6)

**Источник:** 6.2 — Configure EtherChannel

```
interface range gigabitEthernet 0/1 - 2
 channel-group 1 mode active
exit

interface port-channel 1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
exit
```

| Команда | Объяснение | Где |
|---|---|---|
| `interface range gi0/1 - 2` | Выбрать несколько интерфейсов сразу | Коммутаторы |
| `channel-group 1 mode active` | Добавить в EtherChannel группу 1, режим LACP active | DSW1 ↔ DSW2 |
| `channel-group 1 mode desirable` | PAgP режим (Cisco проприетарный) | DSW1 ↔ DSW2 |
| `channel-group 1 mode on` | Статический без переговоров. Обе стороны должны быть `on` | Статический |
| `interface port-channel 1` | Логический интерфейс — на нём настраивать VLAN/trunk | После channel-group |

**Режимы EtherChannel:**

| Протокол | Режим | Описание |
|---|---|---|
| LACP (802.3ad) | `active` | Активно инициирует переговоры |
| LACP | `passive` | Ждёт инициативы |
| PAgP (Cisco) | `desirable` | Активно инициирует |
| PAgP | `auto` | Ждёт инициативы |
| Статический | `on` | Без переговоров |

> [!warning] Порты в EtherChannel должны совпадать по speed, duplex, VLAN, trunk настройкам

---

## Блок 12 — Диагностика и Verification (Book 2, 1.5 и другие)

**Источник:** 1.5 — Verify Directly Connected Networks

---

### Главные show команды

```
show ip interface brief
show ipv6 interface brief
show interfaces gigabitEthernet 0/0
show running-config
show running-config interface gi0/0
show startup-config
show version
show ip route
show ipv6 route
show vlan brief
show interfaces trunk
show port-security
show standby brief
show ip dhcp binding
show etherchannel summary
show mac address-table
show arp
show history
```

| Команда | Объяснение |
|---|---|
| `show ip interface brief` | Кратко: все интерфейсы, IPv4, статус up/down |
| `show ipv6 interface brief` | То же для IPv6 |
| `show interfaces gi0/0` | Полная инфа: счётчики ошибок, duplex, speed, CRC |
| `show running-config` | Текущая активная конфигурация |
| `show running-config interface gi0/0` | Только конфиг конкретного интерфейса |
| `show startup-config` | Сохранённая конфигурация |
| `show version` | Модель, IOS версия, uptime. Ищи `k9` для SSH поддержки |
| `show mac address-table` | MAC адреса и к каким портам привязаны |
| `show arp` | ARP таблица роутера (IP → MAC) |

---

### Фильтры вывода

```
show running-config | section dhcp
show running-config | include hostname
show running-config | begin interface
show ip interface brief | include up
show ip interface brief | exclude up
```

| Фильтр | Объяснение |
|---|---|
| `| section dhcp` | Показать только секцию dhcp |
| `| include up` | Показать только строки с "up" |
| `| exclude up` | Убрать строки с "up" |
| `| begin interface` | Начать вывод с первого вхождения "interface" |
| `terminal length 0` | Отключить постраничный вывод (убрать `--More--`) |

---

### Диагностика соединения

```
ping 10.0.20.1
ping 10.0.20.1 source 10.0.10.1
traceroute 10.0.20.1
ping ipv6 2001:db8:acad:2::1
```

| Команда | Объяснение |
|---|---|
| `ping 10.0.20.1` | ICMP проверка связи. `!` = ответ, `.` = таймаут, `U` = unreachable |
| `ping 10.0.20.1 source 10.0.10.1` | Ping с конкретного source IP — имитирует трафик из VLAN 10 в VLAN 20 |
| `traceroute 10.0.20.1` | Путь пакета через все промежуточные устройства |

---

## Быстрая шпаргалка по паролям

> [!tip] Пробуй в этом порядке при входе на незнакомое устройство

| Пароль | Где используется | Вероятность |
|---|---|---|
| `cisco` | console password, vty password | ★★★★★ |
| `class` | enable secret | ★★★★★ |
| `ccna` | enable secret, username secret | ★★★★☆ |
| `ospf` | console/vty — если устройство OSPF роутер | ★★★★☆ |
| `hsrp` | console/vty — если DSW1/DSW2 | ★★★★☆ |
| `vlan` | console/vty — если коммутатор | ★★★☆☆ |
| `telnet` | vty password | ★★★☆☆ |
| `dhcp` | console/vty — если DHCP сервер | ★★★☆☆ |
| `ssh` | vty password | ★★☆☆☆ |

---

## Статусы интерфейса — что они значат

| Статус | Причина | Решение |
|---|---|---|
| `up / up` | Всё работает | — |
| `down / down` | Нет физического линка | Проверить кабель |
| `administratively down / down` | Выключен командой `shutdown` | `no shutdown` |
| `up / down` | Физика есть, L2 проблема | Проверить протокол, encapsulation |
| `err-disabled` | Сработал Port Security | Перенастроить, `shutdown` → `no shutdown` |

> [!success] Итог
> Все команды взяты из Book 1 и Book 2 — только то что реально проходили. Блоки 1–12 покрывают всю топологию мидтерма от hostname до HSRP.

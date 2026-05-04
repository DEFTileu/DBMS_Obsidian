---
  protected: true
---

#labs

# Lab 10 — VLAN + Inter-VLAN Routing + DHCP + Relay Agent

> [!abstract] Суть лабы
> Настроить VLANы на трёх свитчах (Faculty/Students/Admin/MGMT), Inter-VLAN Routing через Router-on-a-Stick на R1, DHCP сервер на R2 с Relay Agent на R1 для разных подсетей. Проверить полную связность.

## Source

Packet Tracer — задание преподавателя (Week 1)

## Topic

- `VLANs (создание, access/trunk порты)`
- `Inter-VLAN Routing — Router-on-a-Stick`
- `DHCP Server + Relay Agent (ip helper-address)`
- `RIP v2`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/03 - VLANs/03 - VLANs|Book 2 Module 3 — VLANs]]
- [[Book 2. Switching, Routing, and Wireless Essentials/04 - Inter-VLAN Routing/04 - Inter-VLAN Routing|Book 2 Module 4 — Inter-VLAN Routing]]
- [[Book 2. Switching, Routing, and Wireless Essentials/07 - DHCPv4/07 - DHCPv4|Book 2 Module 7 — DHCPv4]]

## Цель

- Создать VLANы 10/20/30/99 на S1, S2, Sw0 и настроить access/trunk порты
- Настроить Router-on-a-Stick субинтерфейсы на R1 (g0/0.10, .20, .30, .99)
- Настроить DHCP пулы на R2 для каждого VLAN
- Настроить `ip helper-address` на R1 для пересылки DHCP запросов к R2
- Настроить RIP v2 на R1 и R2
- Проверить получение IP через DHCP на конечных устройствах

---

> [!abstract] Суть лабы Настроить VLAN на свитчах, Inter-VLAN Routing через Router-on-a-Stick на R1, DHCP сервер на R2 с Relay Agent на R1. Проверить связность между всеми устройствами.

---

## Топология

|Устройство|Роль|
|---|---|
|R1|Router-on-a-Stick + Relay Agent|
|R2|DHCP Server + RIP|
|Internet|Транзитный роутер|
|Sw0|L2 агрегационный свитч|
|S1, S2|L2 access свитчи|

**VLAN (Switch Virtual Interface)** — виртуальный интерфейс коммутатора для управления. #abbreviation

|VLAN ID|NAME|NETWORK|
|---|---|---|
|10|Faculty|192.168.10.0/24|
|20|Students|192.168.20.0/24|
|30|Admin|192.168.30.0/24|
|99|MGMT|192.168.99.0/24|

**Native VLAN** — VLAN, трафик которого передаётся по trunk без тега (untagged). #networkterm

**trunk** — режим порта свитча, который пропускает трафик нескольких VLAN одновременно. #networkterm

**access** — режим порта свитча, который принадлежит только одному VLAN. #networkterm

---

## Step 1 — S1 (11% → 25%)

```
enable
configure terminal
hostname S1

vlan 10
 name Faculty
vlan 20
 name Students
vlan 30
 name Admin
vlan 99
 name MGMT

interface fa0/1
 switchport mode access
 switchport access vlan 10

interface fa0/2
 switchport mode access
 switchport access vlan 20

interface fa0/3
 switchport mode access
 switchport access vlan 30

interface fa0/4
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

interface vlan 99
 ip address 192.168.99.10 255.255.255.0
 no shutdown

ip default-gateway 192.168.99.1
end
```

`switchport mode access` #ciscoIOScommand Переводит порт в режим access — принадлежит только одному VLAN.

`switchport access vlan 10` #ciscoIOScommand Назначает порт в VLAN 10.

`switchport mode trunk` #ciscoIOScommand Переводит порт в режим trunk — пропускает несколько VLAN.

`switchport trunk native vlan 99` #ciscoIOScommand Устанавливает VLAN 99 как native — его трафик идёт без тега.

`switchport trunk allowed vlan 10,20,30,99` #ciscoIOScommand Разрешает только указанные VLAN на trunk порту.

`ip default-gateway 192.168.99.1` #ciscoIOScommand Задаёт шлюз по умолчанию для управляющего трафика свитча.

> [!warning] Частая ошибка fa0/1, fa0/2, fa0/3 на S1/S2 — это ACCESS порты (к конечным устройствам), НЕ trunk. Trunk только fa0/4 (к Sw0).

---

## Step 1 — S2 (25% → 40%)

```
enable
configure terminal
hostname S2

vlan 10
 name Faculty
vlan 20
 name Students
vlan 30
 name Admin
vlan 99
 name MGMT

interface fa0/1
 switchport mode access
 switchport access vlan 10

interface fa0/2
 switchport mode access
 switchport access vlan 20

interface fa0/3
 switchport mode access
 switchport access vlan 30

interface fa0/4
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

interface vlan 99
 ip address 192.168.99.20 255.255.255.0
 no shutdown

ip default-gateway 192.168.99.1
end
```

---

## Step 1 — Sw0 (40%)

```
enable
configure terminal
hostname Sw0

vlan 10
 name Faculty
vlan 20
 name Students
vlan 30
 name Admin
vlan 99
 name MGMT

interface fa0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

interface fa0/2
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

interface fa0/3
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

interface vlan 99
 ip address 192.168.99.254 255.255.255.0
 no shutdown

ip default-gateway 192.168.99.1
end
```

> [!note] Sw0 особенность Sw0 — агрегационный свитч. Все его порты trunk, потому что он соединяет только свитчи и роутер. У него нет access портов.

---

## Step 2 — R1: IP Addressing + Inter-VLAN Routing (55%)

**Router-on-a-Stick** — метод Inter-VLAN Routing, где один физический интерфейс роутера делится на несколько субинтерфейсов, каждый для своего VLAN. #networkterm

**subinterface (субинтерфейс)** — логический интерфейс, созданный на базе физического, работающий с конкретным VLAN через тегирование 802.1Q. #networkterm

```
enable
configure terminal
hostname R1

interface g0/0
 no shutdown

interface g0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0

interface g0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0

interface g0/0.30
 encapsulation dot1Q 30
 ip address 192.168.30.1 255.255.255.0

interface g0/0.99
 encapsulation dot1Q 99
 ip address 192.168.99.1 255.255.255.0

interface g0/1
 ip address 5.132.24.1 255.255.255.248
 no shutdown
end
```

`encapsulation dot1Q 10` #ciscoIOScommand Привязывает субинтерфейс к VLAN 10 через протокол 802.1Q тегирования.

**802.1Q** — стандарт IEEE для тегирования VLAN трафика на trunk каналах. #abbreviation

> [!danger] Exam trap На субинтерфейсе g0/0.99 НЕ пишем `native` — только если задание явно требует. В этой лабе работает без него.

---

## Step 2 — R2: IP Addressing (60%)

```
enable
configure terminal
hostname R2

interface g0/0
 ip address 5.132.24.2 255.255.255.248
 no shutdown

interface g0/1
 ip address 5.132.24.9 255.255.255.248
 no shutdown
end
```

**subnet /29** — подсеть с маской 255.255.255.248, содержит 8 адресов (6 используемых). #networkterm

---

## Step 2 — Internet: IP Addressing

```
enable
configure terminal
hostname Internet

interface g0/0
 ip address 5.132.24.10 255.255.255.248
 no shutdown

interface g0/1
 ip address 10.10.10.1 255.255.255.0
 no shutdown

ip route 0.0.0.0 0.0.0.0 5.132.24.9
end
```

---

## Step 3.1–3.4 — R2: DHCP Server (78%)

**DHCP (Dynamic Host Configuration Protocol)** — протокол автоматической выдачи IP адресов, маски, шлюза и DNS клиентам. #abbreviation

**DHCP pool** — именованный набор настроек, из которого DHCP сервер выдаёт адреса конкретной сети. #networkterm

**excluded-address** — диапазон адресов, зарезервированных и НЕ выдаваемых DHCP сервером. #networkterm

```
enable
configure terminal

ip dhcp excluded-address 192.168.10.1 192.168.10.10
ip dhcp excluded-address 192.168.20.1 192.168.20.10
ip dhcp excluded-address 192.168.30.1 192.168.30.10

ip dhcp pool VL10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 8.8.8.8
 domain-name vl10.com

ip dhcp pool VL20
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
 dns-server 8.8.8.8
 domain-name vl20.com

ip dhcp pool VL30
 network 192.168.30.0 255.255.255.0
 default-router 192.168.30.1
 dns-server 8.8.8.8
 domain-name vl30.com
end
```

`ip dhcp excluded-address 192.168.10.1 192.168.10.10` #ciscoIOScommand Исключает первые 10 адресов из пула — они зарезервированы для роутеров, свитчей и серверов.

`network 192.168.10.0 255.255.255.0` #ciscoIOScommand Указывает сеть, из которой DHCP будет выдавать адреса.

`default-router 192.168.10.1` #ciscoIOScommand Указывает шлюз по умолчанию, который получат клиенты.

`domain-name vl10.com` #ciscoIOScommand Задаёт DNS суффикс домена для клиентов пула.

> [!important] Почему серверы не должны использовать DHCP? В реальной жизни серверы должны иметь **статические IP**, потому что:
> 
> - Клиенты обращаются к серверу по фиксированному адресу
> - При перезагрузке DHCP может выдать другой IP
> - DNS записи перестанут работать
> - Сервисы станут недоступны

---

## Step 3.5 — R1: Relay Agent (82%)

**DHCP Relay Agent** — функция роутера, которая перенаправляет DHCP запросы от клиентов в другой подсети к удалённому DHCP серверу. #networkterm

**ip helper-address** — команда, настраивающая Relay Agent на субинтерфейсе роутера. #networkterm

```
enable
configure terminal

interface g0/0.10
 ip helper-address 5.132.24.2

interface g0/0.20
 ip helper-address 5.132.24.2

interface g0/0.30
 ip helper-address 5.132.24.2
end
```

`ip helper-address 5.132.24.2` #ciscoIOScommand Перенаправляет DHCP broadcast запросы с субинтерфейса на DHCP сервер R2 (5.132.24.2).

> [!tip] Как запомнить Relay Agent = "посредник". Клиент кричит broadcast "дайте мне IP!", роутер слышит и пересылает запрос unicast на DHCP сервер в другой сети.

---

## Step 4 — R1: RIP (85%)

**RIP (Routing Information Protocol)** — динамический протокол маршрутизации на основе дистанции (hop count), версия 2 поддерживает VLSM. #abbreviation

**passive-interface** — интерфейс, на котором RIP не отправляет updates, только получает. Используется на интерфейсах к конечным устройствам. #networkterm

```
enable
configure terminal

router rip
 version 2
 no auto-summary
 network 192.168.10.0
 network 192.168.20.0
 network 192.168.30.0
 network 192.168.99.0
 network 5.132.24.0
 passive-interface g0/0.10
 passive-interface g0/0.20
 passive-interface g0/0.30
 passive-interface g0/0.99
 passive-interface g0/0
 exit
end
```

`no auto-summary` #ciscoIOScommand Отключает автоматическое суммирование маршрутов — необходимо для работы с разными подсетями.

`network 192.168.10.0` #ciscoIOScommand Включает интерфейсы из этой сети в RIP процесс.

`passive-interface g0/0.10` #ciscoIOScommand Запрещает отправку RIP updates через этот субинтерфейс — клиентам они не нужны.

---

## Step 4 — R2: Static Route + RIP (87%)

**default route (маршрут по умолчанию)** — маршрут 0.0.0.0/0, используется когда нет более специфичного маршрута. #networkterm

**default-information originate** — команда RIP, которая распространяет default route соседям. #networkterm

```
enable
configure terminal

ip route 0.0.0.0 0.0.0.0 5.132.24.10

router rip
 version 2
 no auto-summary
 network 5.132.24.0
 network 5.132.24.8
 default-information originate
 exit
end
```

`ip route 0.0.0.0 0.0.0.0 5.132.24.10` #ciscoIOScommand Статический default route — весь неизвестный трафик отправить на Internet роутер.

`default-information originate` #ciscoIOScommand Распространяет default route через RIP к соседям (в данном случае к R1).

---

## Step 4 — Включить DHCP на конечных устройствах (97%)

На каждом устройстве (PC0, PC1, Laptop0, Laptop1, Server0, Server1):

> Desktop → IP Configuration → выбрать **DHCP**

---

## Step 4 — Проверка

`show ip dhcp binding` #ciscoIOScommand Показывает таблицу выданных DHCP адресов: IP, MAC адрес клиента, время аренды.

`show ip dhcp pool` #ciscoIOScommand Показывает статистику пула: сколько адресов выдано, сколько доступно, имя пула.

`show ip route` #ciscoIOScommand Показывает таблицу маршрутизации: все известные сети, как до них добраться (C=connected, R=RIP, S=static).

`show ip interface brief` #ciscoIOScommand Кратко показывает все интерфейсы, их IP адреса и статус (up/down).

`show vlan brief` #ciscoIOScommand Показывает все VLAN на свитче, их имена и назначенные порты.

`show interfaces trunk` #ciscoIOScommand Показывает trunk порты, allowed VLAN и native VLAN.

---

> [!success] Итог Если всё настроено правильно, ты умеешь:
> 
> - Создавать VLAN и назначать порты
> - Настраивать Router-on-a-Stick для Inter-VLAN Routing
> - Настраивать DHCP сервер с несколькими пулами
> - Настраивать Relay Agent для переброски DHCP между подсетями
> - Настраивать RIP v2 с passive interfaces
> - Проверять связность командами show
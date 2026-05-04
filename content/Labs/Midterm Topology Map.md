---
  protected: true
---

#labs

# Мидтерм — Карта топологии и задания

> [!abstract] Топология
> Основана на скриншоте мидтерма. Устройства разделены на 3 зоны: левая (access), центр (core роутеры), правая (distribution + серверы).

---

## Карта устройств

```
[Laptop0] ──── [ASW3: 2960] ──── [ASW1: 2960] ──── [R1: 2911] ════ [R2: 2911] ──── [DSW1: 3650] ──── [ASW-R: 2960] ──── [Server1]
                   │                   │                │    (red)        │                                                    │
               [Server0]          [ASW2: 2960]      [R3: 2911]       [DSW2: 3650] ──────────────────────────────────────── [Server2]
                                   │       │          (red)
                                [Laptop1] [Laptop2]
```

**Красные линии** = WAN/Serial соединения между роутерами (или trunk с другим VLAN).

---

## Зона 1 — Левая сеть (Access Layer)

| Устройство | Тип | Вероятные задания |
|---|---|---|
| **Laptop0** | Конечное устройство | Стартовая точка, DHCP клиент, Telnet цепочки |
| **ASW3** (2960) | Access коммутатор | Port Security на Fa0/1 (к Laptop0), Fa0/2 (к Server0) |
| **Server0** | Сервер | FTP/Telnet цель, DHCP сервер |
| **ASW1** (2960) | Access коммутатор | VLAN assignment, trunk к R1, Port Security |
| **ASW2** (2960) | Access коммутатор | VLAN assignment, Port Security на портах к Laptop1/Laptop2 |
| **Laptop1, Laptop2** | Конечные устройства | DHCP клиенты, тест пинга между VLAN |

### Что настраивать в Зоне 1:

```
── ASW3 ──
! Port Security на Fa0/1 (Laptop0) — sticky или static
! Port Security на Fa0/2 (Server0) — sticky

── ASW1 ──
! vlan 10 / vlan 20 / vlan 30
! Fa0/X → switchport access vlan 10
! Gi0/1 → switchport mode trunk (к R1)
! switchport trunk allowed vlan 10,20,30

── ASW2 ──
! vlan 10 / vlan 20
! Fa0/1 → access vlan 10 (Laptop1)
! Fa0/2 → access vlan 20 (Laptop2)
! Port Security на портах к ноутбукам
```

---

## Зона 2 — Центр (Core / WAN)

| Устройство | Тип | Вероятные задания |
|---|---|---|
| **R1** (2911) | Core роутер | Router-on-a-Stick, OSPF, DHCP сервер, NAT inside |
| **R2** (2911) | WAN роутер | OSPF, Static routes, Serial интерфейс |
| **R3** (2911) | WAN роутер | OSPF, Static routes, точка входа в правую сеть |

### Что настраивать в Зоне 2:

```
── R1 ──
! Inter-VLAN: Gi0/0.10 / .20 / .30 с encapsulation dot1Q
! DHCP pools для VLAN10, VLAN20
! OSPF: network все подключённые сети area 0
! default-information originate (если есть ISP)

── R2 / R3 ──
! OSPF: network X.X.X.X wildcard area 0
! Возможно Serial интерфейс: ip address / clock rate (DCE сторона)
! Telnet доступ (vty password)
```

> [!warning] Serial интерфейс (DCE/DTE)
> Если роутеры соединены Serial кабелем — на DCE стороне нужно `clock rate 64000`.
> ```
> interface serial 0/0/0
>  ip address 10.0.12.1 255.255.255.252
>  clock rate 64000
>  no shutdown
> ```

---

## Зона 3 — Правая сеть (Distribution + Servers)

| Устройство | Тип | Вероятные задания |
|---|---|---|
| **DSW1** (3650) | L3 Distribution | HSRP Active, SVI для VLAN, ip routing, OSPF |
| **DSW2** (3650) | L3 Distribution | HSRP Standby, SVI для VLAN, ip routing |
| **ASW-R** (2960) | Access коммутатор | Trunk к DSW1 и DSW2, Port Security к серверам |
| **Server1, Server2** | Серверы | Финальные цели — FTP/HTTP/Telnet |

### Что настраивать в Зоне 3:

```
── DSW1 ──
! ip routing
! interface vlan 10 / vlan 20 — IP адреса (x.x.x.252)
! standby 1 ip X.X.X.254
! standby 1 priority 110
! standby 1 preempt
! OSPF — добавить VLAN сети и uplink к R3

── DSW2 ──
! ip routing
! interface vlan 10 / vlan 20 — IP адреса (x.x.x.253)
! standby 1 ip X.X.X.254   (тот же виртуальный IP!)
! (без priority — default 100 = Standby)

── ASW-R ──
! Gi0/1 → trunk к DSW1
! Gi0/2 → trunk к DSW2
! Fa0/1 → access vlan X → Server1
! Fa0/2 → access vlan X → Server2
! Port Security на портах к серверам
```

---

## Полная карта вероятных заданий по устройствам

| Устройство | Задание | Вероятность |
|---|---|---|
| ASW3, ASW2 | Port Security (sticky/static) | ★★★★★ |
| ASW1, ASW-R | VLAN + trunk настройка | ★★★★★ |
| R1 | Router-on-a-Stick (сабинтерфейсы) | ★★★★★ |
| DSW1, DSW2 | HSRP (Active/Standby) | ★★★★☆ |
| R1 | DHCP пулы для VLAN | ★★★★☆ |
| R1, R2, R3 | OSPF между роутерами | ★★★★☆ |
| Все устройства | Hostname | ★★★☆☆ |
| R1 | NAT/PAT к ISP | ★★★☆☆ |
| DSW1, DSW2 | SVI + ip routing | ★★★☆☆ |
| R1 / R2 | IPv6 Dual Stack | ★★★☆☆ |
| R1 / ASW | SSH настройка | ★★★☆☆ |
| R1 / ASW-R | Static routes | ★★☆☆☆ |
| DSW1-DSW2 | EtherChannel | ★★☆☆☆ |
| R1 / DSW | ACL фильтрация | ★★☆☆☆ |

---

## Типичный порядок настройки (от простого к сложному)

```
1. Hostname на всех устройствах
2. IP адреса на всех интерфейсах
3. VLAN создание на коммутаторах
4. Access / trunk порты
5. Inter-VLAN routing (R1 сабинтерфейсы) или SVI на DSW
6. OSPF между роутерами
7. DHCP пулы на R1
8. HSRP на DSW1 / DSW2
9. Port Security на access портах
10. NAT если есть ISP
11. SSH если требуется
12. IPv6 если требуется
13. Проверка ping между всеми сегментами
```

> [!success] Финальная проверка
> ```
> ping [VLAN10 gateway] source [VLAN20 host]  → тест Inter-VLAN
> show standby brief                           → тест HSRP
> show ip dhcp binding                         → тест DHCP
> show port-security                           → тест Port Security
> show ip route                                → тест маршрутизации
> ```

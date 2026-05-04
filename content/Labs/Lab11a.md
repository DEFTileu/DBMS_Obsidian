---
  protected: true
---

#labs

# Lab 11a — WLC Configuration (WLAN, DHCP, SNMP)

> [!abstract] Суть лабы
> Создать новый WLAN на Cisco WLC с нуля: настроить VLAN интерфейс, подключить RADIUS сервер для 802.1X аутентификации, создать WLAN профиль с FlexConnect, настроить внутренний DHCP и SNMP мониторинг, подключить беспроводной хост.

## Source

https://drive.google.com/file/d/1PPsIfDkyGzlWsqj_vaiffGDbuYT0o8l/view?usp=drivesdk

## Topic

- `Cisco WLC — создание WLAN профиля`
- `RADIUS / 802.1X / WPA2-Enterprise`
- `FlexConnect (Local Switching + Local Auth)`
- `Internal DHCP на WLC`
- `SNMP Trap Receiver`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/13 - WLAN Configuration/13 - WLAN Configuration|Book 2 Module 13 — WLAN Configuration]]

## Related Files

- [[Labs/Lab11b|Lab 11b — Wireless Troubleshooting]]

## Цель

- Создать VLAN интерфейс `WLAN-5` (VLAN 5) на WLC
- Подключить RADIUS сервер `172.31.1.254` с Shared Secret `Cisco123`
- Создать WLAN `SSID-5` (Floor 2 Employees) с WPA2-Enterprise + FlexConnect
- Настроить внутренний DHCP scope `Wired Management` (диапазон .240–.249)
- Настроить SNMP Trap Receiver `WLAN_SNMP` на `172.31.1.254`
- Подключить Wireless Host через профиль `WLC NET`

---

## Термины

**WLC (Wireless LAN Controller)** — контроллер беспроводной сети Cisco. Централизованно управляет точками доступа и WLAN профилями. #abbreviation

**RADIUS (Remote Authentication Dial-In User Service)** — протокол аутентификации. В Wi-Fi используется для WPA2-Enterprise (802.1X) — каждый пользователь входит с личным логином/паролем. #abbreviation

**Shared Secret** — общий ключ между WLC и RADIUS сервером для взаимной аутентификации. Должен совпадать на обоих устройствах. #networkterm

**AAA (Authentication, Authorization, Accounting)** — система контроля доступа: кто, что, когда делал. #abbreviation

**FlexConnect** — режим работы AP при котором трафик коммутируется локально, а не через WLC. Нужен когда AP и WLC в разных сайтах. #networkterm

**Local Switching** — FlexConnect режим: клиентский трафик идёт напрямую в локальную сеть, минуя WLC. #networkterm

**Local Auth** — FlexConnect режим: аутентификация происходит на AP локально, если WLC недоступен. #networkterm

**WPA2-Enterprise (802.1X)** — метод Wi-Fi аутентификации с индивидуальным логином/паролем через RADIUS. #abbreviation

**DHCP Scope** — именованный диапазон IP адресов на внутреннем DHCP сервере WLC. #networkterm

**SNMP Trap** — уведомление которое устройство само отправляет на сервер мониторинга при событии (AP упала, клиент подключился и т.д.). #networkterm

**VLAN Interface (WLC)** — виртуальный интерфейс на WLC, привязанный к VLAN. Каждый WLAN привязывается к своему интерфейсу. #networkterm

---

## Справка — Credentials

| Устройство        | Адрес           | Login  | Password  |
|-------------------|-----------------|--------|-----------|
| WLC               | 192.168.200.254 | admin  | Cisco123  |
| RADIUS Server     | 172.31.1.254    | —      | —         |
| RADIUS Shared Key | —               | —      | Cisco123  |
| SSID-5 (user1)    | —               | user1  | User1Pass |

---

## Решение

### Part 1 — Создать новый WLAN

#### Шаг 1 — Создать VLAN интерфейс WLAN-5

> Браузер → `https://192.168.200.254` → admin / Cisco123

**Путь:** `Controller → Interfaces → New`

1. Interface Name: `WLAN-5`
2. VLAN ID: `5`
3. **Apply**

**Настройки интерфейса:**

| Поле               | Значение        |
|--------------------|-----------------|
| Port               | 1               |
| IP Address         | 192.168.5.254   |
| Netmask            | 255.255.255.0   |
| Gateway            | 192.168.5.1     |
| Primary DHCP Server| 192.168.5.1     |

4. Заполни поля → **Apply** → **Save Configuration**

> [!note] Primary DHCP Server
> `192.168.5.1` — это шлюз VLAN 5. WLC будет перенаправлять DHCP запросы от клиентов на этот адрес.

---

#### Шаг 2 — Настроить RADIUS сервер

**Путь:** `Security → AAA → RADIUS → Authentication → New`

1. Server IP: `172.31.1.254`
2. Shared Secret: `Cisco123`
3. **Apply**

> [!warning] Shared Secret должен совпадать
> Одинаковый ключ прописывается и на WLC и на RADIUS сервере. Если не совпадает — 802.1X не работает.

---

#### Шаг 3 — Создать WLAN

**Путь:** `WLANs → Create New → Go`

1. Profile Name: `Floor 2 Employees`
2. SSID: `SSID-5`
3. ID: `5`
4. **Apply**

**General настройки:**
5. ✅ Enabled
6. Interface: `WLAN-5`

**FlexConnect (вкладка Advanced):**
7. FlexConnect → ✅ **Local Switching**
8. ✅ **Local Auth**
9. **Apply**

> [!note] Зачем FlexConnect Local Switching?
> Без него весь трафик клиентов идёт через WLC (централизованно). С ним — трафик коммутируется локально на AP, снижая нагрузку на WLC и WAN.

---

#### Шаг 4 — Настроить безопасность WLAN

**Путь:** вкладка `Security → Layer 2`

1. Выбери `WPA+WPA2`
2. ✅ **WPA2 Policy**
3. Auth Key Mgmt: `802.1X`
4. Вкладка **AAA Servers** → Server 1: `172.31.1.254`
5. **Apply**

> [!danger] Порядок важен
> RADIUS сервер нужно добавить в Шаге 2 **до** того как назначать его в AAA Servers. Иначе он не появится в списке.

---

### Part 2 — DHCP и SNMP

#### Шаг 1 — Настроить внутренний DHCP

**Путь:** `Controller → Interfaces → Management`

1. Primary DHCP: изменить на `192.168.200.254` (сам WLC)
2. **Apply** → **Save**

**Путь:** `Controller → Internal DHCP Server → DHCP Scope → New`

3. Имя scope: `Wired Management`
4. **Apply**

| Поле       | Значение          |
|------------|-------------------|
| Pool Start | 192.168.200.240   |
| Pool End   | 192.168.200.249   |
| Status     | Enabled           |

5. **Apply** → **Save Configuration**

> [!note] Этот scope — для Management сети
> Диапазон `.240–.249` (10 адресов) для управляющих устройств (Admin PC и др.), не для беспроводных клиентов WLAN-5.

---

#### Шаг 2 — SNMP Trap Receiver

**Путь:** `Management → SNMP → Trap Receivers → New`

1. Community: `WLAN_SNMP`
2. IP Address: `172.31.1.254`
3. **Apply**

> [!tip] Что такое SNMP Community?
> Строка-пароль для SNMP v1/v2c. Сервер мониторинга использует тот же community string для приёма trap'ов от WLC.

---

### Part 3 — Подключить Wireless Host

**Wireless Host → Desktop → PC Wireless → Profiles → New**

1. Profile Name: `WLC NET` → **Next**
2. Выбери сеть **SSID-5** → **Advanced Setup** → **Next**
3. IP Configuration: **DHCP** → **Next**
4. Security: **WPA2-Enterprise** → **Next**
5. Login: `user1`
6. Password: `User1Pass`
7. **Save** → **Connect to Network**

> [!danger] Регистр важен!
> `user1` / `User1Pass` — вводи точно. `User1` и `user1` — разные учётные данные.

---

## Полный порядок выполнения

```
Part 1:
1. Controller → Interfaces → создать WLAN-5 (VLAN 5, IP 192.168.5.254)
2. Security → RADIUS → добавить 172.31.1.254 / Cisco123
3. WLANs → создать SSID-5 (Floor 2 Employees) → привязать WLAN-5
4. WLAN Advanced → FlexConnect: Local Switching + Local Auth
5. WLAN Security → WPA2 + 802.1X + RADIUS сервер 172.31.1.254

Part 2:
6. Management Interface → Primary DHCP = 192.168.200.254
7. Internal DHCP → scope Wired Management (.240-.249)
8. SNMP → Trap Receiver → WLAN_SNMP / 172.31.1.254

Part 3:
9. Wireless Host → PC Wireless → Profile WLC NET → SSID-5 → user1/User1Pass
```

---

> [!success] Итог
> Если понял лабу — умеешь создать WLAN на WLC с нуля: VLAN интерфейс → RADIUS → WLAN профиль → FlexConnect → DHCP scope → SNMP → подключение клиента через WPA2-Enterprise.

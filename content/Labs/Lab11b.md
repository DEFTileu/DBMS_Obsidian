---
  protected: true
---

#labs

# Lab 11b — Wireless Networks Troubleshooting

> [!abstract] Суть лабы
> Диагностировать и исправить проблемы в двух сетях. **Home Network** — DNS, DHCP и WAN интерфейс домашнего роутера. **Enterprise Network** — WLC: WLAN выключен, неправильный тип аутентификации, неверные credentials на клиентах.

## Topic

- `Wireless Troubleshooting`
- `Home Router — DNS, DHCP, WAN`
- `Cisco WLC — WLAN Enable/Disable, PSK vs 802.1X`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/13 - WLAN Configuration/13 - WLAN Configuration|Book 2 Module 13 — WLAN Configuration]]

## Related Files

- [[Labs/Lab11a|Lab 11a — WLC Configuration]]

## Цель

**Home Network:**
- Исправить WAN интерфейс роутера (Static → DHCP от провайдера)
- Исправить DNS адрес в DHCP настройках роутера
- Переключить Tablet PC со Static IP на DHCP

**Enterprise Network:**
- Включить WLAN Wireless VLAN 20 на WLC
- Изменить SSID-10 с 802.1X на PSK (Cisco123)
- Исправить credentials на Laptop 2 (SSID-20: user2/User2Pass)
- Подключить Laptop 1 к SSID-10 с новым паролем

---

---

## Термины

**DHCP (Dynamic Host Configuration Protocol)** — протокол автоматической выдачи IP адресов, маски, шлюза и DNS клиентам сети. #abbreviation

**DNS (Domain Name System)** — система которая переводит доменные имена (google.com) в IP адреса. #abbreviation

**WLC (Wireless LAN Controller)** — контроллер беспроводной сети Cisco. Централизованно управляет точками доступа и WLAN профилями. #abbreviation

**WLAN (Wireless Local Area Network)** — беспроводная локальная сеть. #abbreviation

**SSID (Service Set Identifier)** — имя беспроводной сети, которое видят устройства при поиске Wi-Fi. #abbreviation

**WPA2-PSK (Pre-Shared Key)** — метод аутентификации Wi-Fi с общим паролем для всех пользователей. #abbreviation

**WPA2-Enterprise (802.1X)** — метод аутентификации Wi-Fi с индивидуальным логином и паролем для каждого пользователя. Используется в корпоративных сетях. #abbreviation

**802.1X** — стандарт аутентификации на уровне порта. В беспроводных сетях используется для WPA2-Enterprise. #abbreviation

**Static IP** — фиксированный IP адрес назначенный вручную, в отличие от динамического через DHCP. #networkterm

**VLAN (Virtual Local Area Network)** — логическая изоляция сети. В беспроводных сетях каждый SSID обычно привязан к своему VLAN. #abbreviation

> [!note] PSK vs Enterprise **PSK** — один пароль для всех, подходит для дома и малого бизнеса. **Enterprise (802.1X)** — каждый пользователь входит со своим логином/паролем через RADIUS сервер. Используется в крупных компаниях.

---

## 🟡 HOME NETWORK

> [!abstract] Топология Home Wireless Router → подключён к ISP через WAN интерфейс. Клиенты: Smartphone, Tablet PC, Laptop — подключаются по Wi-Fi.

---

### Проблема 1 — Неправильный DNS на роутере

**Затронутые устройства:** Smartphone, Tablet PC, Laptop

**Симптом:** Устройства получают IP через DHCP, но сайты не открываются (DNS не резолвит).

**Решение:**

> 1. Открой браузер на любом устройстве
> 2. Перейди на `192.168.0.1`
> 3. Логин: `admin` / Пароль: `admin`
> 4. Найди раздел **DHCP Settings**
> 5. Поле **Static DNS** → изменить на `10.100.100.254`
> 6. Нажми **Save**

> [!warning] Почему DNS важен? Даже если интернет работает — без правильного DNS адреса устройства не могут открыть ни один сайт по имени. Пинг по IP будет работать, по домену — нет.

---

### Проблема 2 — Tablet PC со статическим IP вместо DHCP

**Затронутое устройство:** Tablet PC

**Симптом:** Tablet PC не получает IP от роутера, использует статически прописанный адрес.

**Решение:**

> 1. Открой **Tablet PC**
> 2. Desktop → **IP Configuration**
> 3. Переключи с **Static** на **DHCP**
> 4. Устройство автоматически получит IP от роутера

> [!tip] Как проверить? После переключения на DHCP поля IP Address, Subnet Mask, Gateway и DNS должны заполниться автоматически.

---

### Проблема 3 — Internet интерфейс роутера со статическим IP

**Затронутое устройство:** Home Wireless Router

**Симптом:** Роутер не получает WAN адрес от провайдера — интернета нет ни у кого.

**Решение:**

> 1. Зайди на `192.168.0.1` (admin/admin)
> 2. Раздел **Setup** → **Internet Connection Type**
> 3. Измени на **Automatic Configuration - DHCP**
> 4. Нажми **Save**

> [!important] Это первое что нужно исправить! Если WAN интерфейс роутера не получает IP от провайдера — весь интернет не работает, независимо от настроек DNS или DHCP на клиентах.

---

### ✅ Порядок исправления Home Network

```
1. Роутер WAN → Automatic DHCP       (интернет появится)
2. Router DHCP Settings → DNS исправить  (сайты откроются)
3. Tablet PC → переключить на DHCP   (планшет получит IP)
```

---

## 🟢 ENTERPRISE NETWORK

> [!abstract] Топология WLC (192.168.200.254) управляет точками доступа. SSID-10 → VLAN 10 → WPA2-PSK SSID-20 → VLAN 20 → WPA2-Enterprise (802.1X) Клиенты: Laptop 1 (SSID-10), Laptop 2 (SSID-20)

---

### Проблема 1 — WLAN Wireless VLAN 20 выключен

**Затронутое устройство:** WLC, все клиенты SSID-20

**Симптом:** SSID-20 не виден в списке сетей — WLAN отключён на контроллере.

**Решение:**

> 1. Открой браузер → перейди на `192.168.200.254`
> 2. Войди в WLC
> 3. Раздел **WLANs**
> 4. Найди **Wireless VLAN 20**
> 5. Поставь галочку ✅ **Enabled**
> 6. Нажми **Apply**

---

### Проблема 2 — Неправильный username на Laptop 2

**Затронутое устройство:** Laptop 2

**Симптом:** Laptop 2 не может подключиться к SSID-20 — неверные учётные данные.

**Решение:**

> 1. Открой **Laptop 2**
> 2. Desktop → **PC Wireless**
> 3. Раздел **Profiles**
> 4. Найди профиль **SSID-20** → нажми **Edit**
> 5. Пройди до шага **Advanced Setup**
> 6. Security: **WPA2-Enterprise**
> 7. Login: `user2`
> 8. Password: `User2Pass`
> 9. Сохрани профиль

> [!danger] Учётные данные чувствительны к регистру! `user2` ≠ `User2` — вводи точно как указано: `user2` / `User2Pass`

---

### Проблема 3 — SSID-10 использует 802.1X вместо PSK

**Затронутое устройство:** WLC

**Симптом:** SSID-10 настроен на Enterprise аутентификацию (802.1X), хотя должен использовать простой пароль (PSK).

**Решение:**

> 1. WLC → `192.168.200.254`
> 2. Раздел **WLANs** → **Wireless VLAN 10**
> 3. Вкладка **Security** → **Layer 2**
> 4. Отключить **802.1X**
> 5. Включить **PSK** (WPA2-Personal)
> 6. Пароль: `Cisco123`
> 7. Нажми **Apply**

> [!warning] 802.1X требует RADIUS сервер Если 802.1X включён, но RADIUS сервер не настроен или недоступен — ни один клиент не подключится к сети, даже с правильным паролем.

---

### Проблема 4 — Laptop 1 не может подключиться к SSID-10

**Затронутое устройство:** Laptop 1

**Симптом:** После исправления WLC нужно обновить профиль подключения на Laptop 1.

**Решение:**

> 1. Открой **Laptop 1**
> 2. Desktop → **PC Wireless**
> 3. Вкладка **Connect**
> 4. Найди **SSID-10** в списке сетей
> 5. Security: **WPA-Personal**
> 6. Pre-shared Key: `Cisco123`
> 7. Нажми **Connect**

---

### ✅ Порядок исправления Enterprise Network

```
1. WLC → включить WLAN Wireless VLAN 20      (SSID-20 появится)
2. WLC → SSID-10 Security → PSK, пароль Cisco123  (исправить тип auth)
3. Laptop 2 → Profile SSID-20 → user2/User2Pass   (правильные credentials)
4. Laptop 1 → Connect SSID-10 → Cisco123          (подключиться)
```

---

## Справка — Credentials

|Устройство|Адрес|Login|Password|
|---|---|---|---|
|Home Router|192.168.0.1|admin|admin|
|WLC|192.168.200.254|—|—|
|SSID-10 (PSK)|—|—|Cisco123|
|SSID-20 (user2)|—|user2|User2Pass|

---

> [!success] Итог — если понял лабу, умеешь:
> 
> - Диагностировать проблемы DHCP/DNS на домашнем роутере
> - Управлять WLAN профилями через Cisco WLC
> - Различать WPA2-PSK и WPA2-Enterprise и настраивать оба режима
> - Настраивать беспроводные профили на клиентских устройствах
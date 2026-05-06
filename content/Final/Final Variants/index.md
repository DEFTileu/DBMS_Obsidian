---
tags:
  - финал
  - варианты
---

# Финальные Варианты — Навигация

> [!warning] На основе реальной топологии
> Все варианты основаны на `img.png` (топология финала) 
> Изучи **все 4 варианта** — финал будет комбинацией из них.

---

## Что точно будет на финале

По информации от одногруппников:

- ✅ **SSH или Telnet** — нет консольного кабеля, доступ только через сеть
- ✅ **WLC (Wireless LAN Controller)** — настройка WLAN
- ✅ **3 ноутбука без кабелей** — подключатся по Wi-Fi к WLC
- ✅ **WLAN + DHCP + VLAN + Inter-VLAN Routing** — все четыре темы вместе

---

## Варианты

| Вариант | Главные темы | Сложность | Вероятность |
|---|---|---|---|
| [[Final/Final Variants/Variant 1 — VLAN + Inter-VLAN + DHCP + WLC PSK + SSH\|Вариант 1]] | VLAN + Inter-VLAN + DHCP + WLC PSK + SSH | ⭐⭐⭐ | Высокая |
| [[Final/Final Variants/Variant 2 — WLC RADIUS 802.1X + VLAN + DHCP Relay + SSH\|Вариант 2]] | WLC RADIUS 802.1X + DHCP Relay + SSH | ⭐⭐⭐⭐ | Средняя |
| [[Final/Final Variants/Variant 3 — Telnet Chain + SSH + VLAN + WLC PSK\|Вариант 3]] | Telnet chain + SSH + VLAN + WLC PSK | ⭐⭐⭐ | Средняя |
| [[Final/Final Variants/Variant 4 — Full Enterprise (All Topics)\|Вариант 4]] | Всё вместе с прогрессом по % | ⭐⭐⭐⭐⭐ | Подготовка |

---

## Критические команды — Быстрая шпаргалка

### SSH (порядок строгий!)
```cisco
hostname NAME              ! 1. hostname не default
ip domain-name cisco.com   ! 2. domain ОБЯЗАТЕЛЬНО
crypto key generate rsa    ! 3. только теперь ключи (1024 бит)
ip ssh version 2           ! 4. SSHv2
username admin secret cisco ! 5. пользователь
line vty 0 15              ! 6. VTY
 transport input ssh
 login local
```

### Inter-VLAN на L3 коммутаторе (3650)
```cisco
ip routing                 ! ОБЯЗАТЕЛЬНО — без него нет маршрутизации
interface Vlan10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
```

### WLC — Порядок действий (GUI)
```
1. Controller → Interfaces → New  (создать VLAN Interface)
2. Security → RADIUS → New        (если 802.1X — добавить RADIUS сервер)
3. WLANs → Create New             (создать WLAN профиль)
4. WLAN General → ✅ Enabled + Interface
5. WLAN Security → WPA2 + PSK/802.1X
6. Apply → Save Configuration
```

### DHCP
```cisco
ip dhcp excluded-address 192.168.x.1 192.168.x.10
ip dhcp pool POOLNAME
 network 192.168.x.0 255.255.255.0
 default-router 192.168.x.1
 dns-server 8.8.8.8
```

---

## Возможные пароли на финале

| Устройство | Login | Password |
|---|---|---|
| Все коммутаторы — Enable | — | `cisco` или `class` |
| Telnet VTY | — | `cisco` |
| SSH | `admin` | `cisco` или `Cisco123` |
| WLC GUI | `admin` | `Cisco123` |
| RADIUS Shared Key | — | `Cisco123` |
| WLAN PSK | — | `Cisco123` |
| WLAN 802.1X юзер | `user1` | `User1Pass` |

---

## Топ-5 ошибок которые всех валят

1. **Нет `ip routing`** на L3 коммутаторе → Inter-VLAN не работает
2. **Неправильный порядок SSH** → `crypto key generate rsa` не работает без `ip domain-name`
3. **RADIUS не добавлен в Security раньше WLAN** → не появится в списке AAA Servers
4. **Нет `ip default-gateway`** на L2 коммутаторе → нет управления через сеть
5. **Нет `no shutdown`** на SVI → интерфейс down, нет связи

---

> [!tip] Стратегия сдачи
> Начни с базовой конфигурации → потом VLAN → потом routing → потом DHCP → потом SSH → в конце WLC. Каждый шаг проверяй `show` командой. Не переходи дальше пока предыдущий шаг не работает.

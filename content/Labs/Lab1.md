---
  protected: true
---

#labs

# Lab 1 — Cisco Basic IOS Configurations

> [!abstract] Суть лабы
> Настроить два коммутатора S1 и S2 с нуля: hostname, пароли, SVI, banner, service password-encryption. Восстановить пароль на R1 через ROMMON. Найти IP скрытого коммутатора S3 и подключиться к нему через Telnet, чтобы достать FLAG.

## Source

https://drive.google.com/file/d/12JEAVTPlrxK2Xl1zhe7bP7jYF51hOLbt/view

## Topic

- `Basic IOS Configuration (hostname, passwords, banner, SVI)`
- `Password Recovery через ROMMON`
- `Telnet access`

## Related Book Modules

- [[Book 1. Introduction to Networks/02 - Basic Switch and End Devices Configuration/02 - Basic Switch and End Devices Configuration|Book 1 Module 2 — Basic Switch and End Devices Configuration]]
- [[Book 2. Switching, Routing, and Wireless Essentials/01 - Basic Device Configuration/01 - Basic Device Configuration|Book 2 Module 1 — Basic Device Configuration]]

## Цель

- Задать IP на PC1 и PC2 по таблице адресации
- Настроить S1 (hostname, пароли, SVI, banner) → 45%
- Настроить S2 аналогично → 70%
- Восстановить пароль на R1 через ROMMON → 72%
- Настроить интерфейсы R1 → 86%
- Найти IP S3 и подключиться через Telnet → 89%
- Достать FLAG с S3 → 100%

---

## Топология и адресация

| Device | Interface | IP Address  | Subnet Mask   | Default Gateway |
|--------|-----------|-------------|---------------|-----------------|
| S1     | VLAN 1    | 10.44.0.1   | 255.255.255.0 | 10.44.0.254     |
| S2     | VLAN 1    | 10.44.0.2   | 255.255.255.0 | 10.44.0.254     |
| PC1    | NIC       | 10.44.0.10  | 255.255.255.0 | 10.44.0.254     |
| PC2    | NIC       | 10.44.0.20  | 255.255.255.0 | 10.44.0.254     |
| R1     | G0/0      | 10.44.0.254 | 255.255.255.0 | —               |

---

## Термины

**SVI (Switch Virtual Interface)** — виртуальный интерфейс коммутатора для управления. Назначается IP адрес для доступа по сети. #abbreviation

**service password-encryption** — команда шифрующая все пароли в running-config (type 7). Слабое шифрование, но скрывает пароли от беглого взгляда. #networkterm

**ROMMON (ROM Monitor)** — низкоуровневый режим загрузки Cisco. Используется для восстановления пароля и других аварийных операций. #networkterm

**config-register** — регистр конфигурации, определяющий режим загрузки IOS. `0x2142` — загрузить без startup-config, `0x2102` — стандартный. #networkterm

**banner motd** — сообщение дня, которое отображается при подключении к устройству. #networkterm

---

## Решение

### Шаг 1 — PC1 и PC2: задать IP (8%)

PC → Desktop → IP Configuration → выбрать **Static** → ввести по таблице адресации.

---

### Шаг 2 — Настройка S1 (→ 45%)

```cisco
enable
configure terminal
hostname teach
line console 0
 password dog
 login
 exit
enable password craft
line vty 0 15
 password lecture
 login
 exit
banner motd # Authorized Users Only #
service password-encryption
interface vlan 1
 ip address 10.44.0.1 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.44.0.254
copy running-config startup-config
```

`hostname teach` #ciscoIOScommand Задаёт имя устройства.

`line console 0` → `password dog` → `login` #ciscoIOScommand Пароль для физического подключения через консольный кабель.

`enable password craft` #ciscoIOScommand Пароль для перехода в privileged EXEC mode. (Незашифрованный — для старых лаб.)

`line vty 0 15` → `password lecture` → `login` #ciscoIOScommand Пароль для удалённого подключения (Telnet/SSH). `0 15` = 16 одновременных сессий.

`service password-encryption` #ciscoIOScommand Шифрует все пароли в running-config (type 7). Применяется ко всем уже настроенным паролям.

`ip default-gateway 10.44.0.254` #ciscoIOScommand Шлюз для самого коммутатора — нужен для управления из другой сети.

`copy running-config startup-config` #ciscoIOScommand Сохраняет конфигурацию в NVRAM. Без этого конфиг потеряется при перезагрузке.

> [!warning] Частая ошибка
> `copy running-config startup-config` = то же самое что `write memory`. Не забудь сохранить!

---

### Шаг 3 — Настройка S2 (→ 70%)

```cisco
enable
configure terminal
hostname data
line console 0
 password snake
 login
 exit
enable password thrive
line vty 0 15
 password tv
 login
 exit
banner motd # Authorized Users Only #
service password-encryption
interface vlan 1
 ip address 10.44.0.2 255.255.255.0
 no shutdown
 exit
ip default-gateway 10.44.0.254
copy running-config startup-config
```

> [!note] S1 и S2 — одинаковая структура
> Команды одинаковые, но разные: hostname, пароли и IP адрес SVI. Сверяйся с таблицей.

---

### Шаг 4 — Сброс пароля R1 через ROMMON (→ 72%)

> [!important] Зачем ROMMON?
> Если забыл пароль на роутере — зайти в CLI невозможно. ROMMON позволяет обойти startup-config при загрузке и сбросить пароль.

```
1. Выключи R1 → включи → нажми Ctrl+Break сразу после включения
   (попадёшь в ROMMON)

2. В ROMMON:
   confreg 0x2142
   reset

3. После перезагрузки (без конфига):
   enable
   copy startup-config running-config

4. В configure terminal:
   line console 0
    exec-timeout 0 0
    exit
   hostname R1
   config-register 0x2102
   copy running-config startup-config
```

`confreg 0x2142` #ciscoIOScommand В ROMMON — говорит роутеру загрузиться пропуская startup-config. Пароли не применяются.

`config-register 0x2102` #ciscoIOScommand Возвращает нормальный режим загрузки. Обязательно вернуть после восстановления!

> [!danger] Exam Trap
> Если не вернуть `config-register 0x2102` — роутер будет всегда загружаться без startup-config. Конфиг теряется при каждой перезагрузке.

---

### Шаг 5 — Настройка R1 (→ 86%)

```cisco
configure terminal
interface gigabitEthernet 0/0
 ip address 10.44.0.254 255.255.255.0
 no shutdown
 exit
interface gigabitEthernet 0/1
 ip address 192.168.1.254 255.255.0.0
 no shutdown
 exit
copy running-config startup-config
```

---

### Шаг 6 — Найти IP скрытого S3

```cisco
ping 0.0.0.0
```

`ping 0.0.0.0` #ciscoIOScommand Особый трюк: ping на 0.0.0.0 показывает IP самого устройства. Позволяет найти IP S3 не заходя в его конфиг.

> IP S3 = **192.168.23.147**

---

### Шаг 7 — Подключиться к S3 и достать FLAG (→ 100%)

```
telnet 192.168.23.147
```
Пароль: `cisco123`

```cisco
copy flash: running-config
Source filename []? flag.txt
Destination filename [running-config]? (Enter)

show running-config
```

> [!success] FLAG
> Флаг находится в description интерфейсов: **`INF_313{MY_FIRST_FLAG}`**

---

## Проверка

```cisco
show running-config
show ip interface brief
show interfaces vlan 1
```

`show ip interface brief` #ciscoIOScommand Быстро проверяет статус всех интерфейсов. SVI должен быть up/up с нужным IP.

> [!tip] Memory Hook
> Порядок настройки switch: hostname → пароли → banner → service password-encryption → SVI → gateway → save. Всегда одинаковый, меняются только значения.

---

> [!success] Итог
> Если понял лабу — умеешь настроить switch с нуля, восстановить пароль через ROMMON и подключаться к удалённым устройствам через Telnet.

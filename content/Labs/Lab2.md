---
  protected: true
---


#labs

# Lab 2 — Basic IOS Configuration

> [!abstract] Суть лабы
> Базовая настройка IOS на switches и router: hostname, пароли, banner, SSH/Telnet доступ, SVI и default gateway. Та же основа что и Lab 1, но на другой топологии.

## Source

https://drive.google.com/file/d/1zOGBUG6ZMChYpGwQ6Do_ItRIfsNOq/view?usp=drivesdk

## Topic

- `Basic IOS Configuration`
- `Hostname, passwords, banner`
- `SSH / Telnet`
- `SVI и default gateway`

## Related Book Modules

- [[Book 1. Introduction to Networks/02 - Basic Switch and End Devices Configuration/02 - Basic Switch and End Devices Configuration|Book 1 Module 2 — Basic Switch and End Devices Configuration]]
- [[Book 2. Switching, Routing, and Wireless Essentials/01 - Basic Device Configuration/01 - Basic Device Configuration|Book 2 Module 1 — Basic Device Configuration]]

## Цель

- Задать hostname, enable secret, пароли на console и vty
- Настроить banner motd
- Настроить SVI и default-gateway на switch
- Проверить SSH/Telnet подключение

---

## Термины

**SVI (Switch Virtual Interface)** — виртуальный интерфейс коммутатора для управления. Назначается IP адрес для доступа по SSH/Telnet. #abbreviation

**enable secret** — зашифрованный пароль для входа в privileged EXEC mode (`enable`). Всегда предпочтительнее `enable password`. #networkterm

**banner motd** — сообщение дня, которое показывается при подключении к устройству. MOTD = Message Of The Day. #networkterm

**default-gateway** — адрес роутера, на который коммутатор отправляет трафик для других сетей. Нужен для управления свичом удалённо. #networkterm

---

## Решение

### Порядок настройки switch (всегда одинаковый)

```cisco
enable
configure terminal
hostname SW1
no ip domain-lookup

enable secret cisco

line console 0
 password cisco
 login
 logging synchronous
 exit

line vty 0 4
 password cisco
 login
 transport input ssh telnet
 exit

banner motd # Authorized Access Only #

interface vlan 1
 ip address 192.168.1.1 255.255.255.0
 no shutdown
 exit

ip default-gateway 192.168.1.254
end
write memory
```

`hostname SW1` #ciscoIOScommand Задаёт имя устройства — отображается в CLI приглашении.

`no ip domain-lookup` #ciscoIOScommand Отключает DNS поиск. Без этого опечатка в команде вызывает долгое ожидание.

`enable secret cisco` #ciscoIOScommand Зашифрованный пароль для privileged mode. Приоритет над `enable password`.

`logging synchronous` #ciscoIOScommand Системные сообщения не прерывают ввод команд.

`transport input ssh telnet` #ciscoIOScommand Разрешает подключение по SSH и Telnet на линиях vty.

`interface vlan 1` → `ip address` #ciscoIOScommand Назначает IP адрес на SVI для управления коммутатором.

`ip default-gateway 192.168.1.254` #ciscoIOScommand Шлюз по умолчанию для самого коммутатора — нужен для ответов из других подсетей.

`write memory` #ciscoIOScommand Сохраняет running-config в startup-config.

### Проверка

```cisco
show running-config
show ip interface brief
show interfaces vlan 1
```

`show ip interface brief` #ciscoIOScommand Проверяет что SVI в состоянии up/up и имеет нужный IP.

> [!tip] Memory Hook
> Порядок: hostname → no domain-lookup → enable secret → console → vty → banner → SVI → gateway → write. Всегда одинаковый.

> [!warning] Частая ошибка
> Без `ip default-gateway` switch не отвечает на ping из другой сети — даже если SVI настроен правильно.

> [!danger] Exam Trap
> `enable secret` **шифрует** пароль в running-config. `enable password` — нет. Если оба настроены, `enable secret` всегда побеждает.

---

> [!success] Итог
> Если понял лабу — умеешь настроить любое Cisco устройство с нуля: hostname, пароли, удалённый доступ, SVI.

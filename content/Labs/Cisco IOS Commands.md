---
  protected: true
---



#computernetworks
#book1
#book2

# Cisco IOS Commands

Эта заметка нужна, чтобы быстро понять: **где вводится команда**, **на каком устройстве она встречается** и **за что отвечает**.

> [!abstract] Суть темы
> В Cisco IOS мало просто помнить команду. На exam часто важно понимать, в каком **mode** ты находишься, на каком **device** работаешь и какой результат команда должна дать.

## Основные термины

**Cisco IOS (Internetwork Operating System)** — операционная система Cisco devices, где ты вводишь команды для настройки и проверки. #abbreviation

**User EXEC mode** — начальный режим после входа в устройство. Здесь доступны базовые команды просмотра. Промпт обычно заканчивается на `>`. #networkterm

**Privileged EXEC mode** — режим расширенного управления устройством. Промпт обычно заканчивается на `#`. #networkterm

**global configuration mode** — режим, где меняют общие настройки устройства. #networkterm

**interface configuration mode** — режим настройки конкретного interface. #networkterm

**line configuration mode** — режим настройки console или VTY lines для доступа к устройству. #networkterm

**SVI (Switch Virtual Interface)** — виртуальный интерфейс коммутатора, например `interface vlan 1`, через который switch получает management IP address. #abbreviation

**VTY (Virtual Teletype)** — виртуальные линии для удалённого доступа по Telnet или SSH. #abbreviation

## Где обычно используются команды

|Команда или режим|Где используется|Где вводится|За что отвечает|
|---|---|---|---|
|`enable`|switch, router|User EXEC|Переход в Privileged EXEC mode|
|`configure terminal`|switch, router|Privileged EXEC|Переход в global configuration mode|
|`interface g0/0/0`|switch, router|Global config|Переход к настройке физического interface|
|`interface vlan 1`|обычно L2 switch|Global config|Переход к настройке SVI для management|
|`line console 0`|switch, router|Global config|Настройка локального console access|
|`line vty 0 15`|switch, router|Global config|Настройка удалённого доступа|
|`show ...` команды|switch, router|Privileged EXEC|Проверка состояния и конфигурации|
|`copy running-config startup-config`|switch, router|Privileged EXEC|Сохранение текущей конфигурации|

## 1. Команды навигации по IOS

```bash
enable
configure terminal
interface g0/0/0
interface vlan 1
line console 0
line vty 0 15
exit
end
disable
```

`enable` #ciscoIOScommand
Переводит устройство из User EXEC mode в Privileged EXEC mode. Обычно это первая команда после входа.

Где используется: на switch и router, когда нужен доступ к show-командам и конфигурации.

`configure terminal` #ciscoIOScommand
Открывает global configuration mode. С этого режима начинается почти вся настройка устройства.

Где используется: на switch и router после `enable`.

`interface g0/0/0` #ciscoIOScommand
Открывает interface configuration mode для конкретного физического порта.

Где используется: на router и switch, когда нужно настроить port, IP address, description или `no shutdown`.

`interface vlan 1` #ciscoIOScommand
Открывает настройку SVI. На L2 switch через этот интерфейс часто задают management IP.

Где используется: в основном на Layer 2 switch.

`line console 0` #ciscoIOScommand
Переходит в режим настройки console line.

Где используется: на switch и router, когда нужно задать пароль для физического доступа через console cable.

`line vty 0 15` #ciscoIOScommand
Переходит в режим настройки виртуальных линий для удалённого входа.

Где используется: на switch и router для Telnet или SSH access.

`exit` #ciscoIOScommand
Выходит на один уровень выше по иерархии режимов.

Где используется: почти везде внутри IOS.

`end` #ciscoIOScommand
Сразу возвращает в Privileged EXEC mode из любого config mode.

Где используется: удобно после серии настроек.

`disable` #ciscoIOScommand
Возвращает устройство из Privileged EXEC mode обратно в User EXEC mode.

Где используется: реже, в основном для выхода из привилегированного режима.

## 2. Базовая настройка устройства

```bash
hostname S1
enable secret class
service password-encryption
banner motd #Authorized Access Only#
username admin secret Cisco123!
ip domain-name lab.local
```

`hostname S1` #ciscoIOScommand
Меняет имя устройства. После этого меняется prompt, и становится понятно, к какому device ты подключён.

Где используется: на switch и router в global configuration mode.

`enable secret class` #ciscoIOScommand
Задаёт пароль для команды `enable`, то есть для входа в Privileged EXEC mode.

Где используется: на switch и router.

`service password-encryption` #ciscoIOScommand
Включает шифрование паролей в конфигурации, чтобы они не были видны открытым текстом в `show running-config`.

Где используется: на switch и router как базовая мера защиты.

`banner motd #Authorized Access Only#` #ciscoIOScommand
Настраивает message of the day, которое видит пользователь при подключении.

Где используется: на switch и router для предупреждения о доступе только для авторизованных пользователей.

`username admin secret Cisco123!` #ciscoIOScommand
Создаёт локального пользователя с секретом.

Где используется: на switch и router, особенно перед настройкой SSH и `login local`.

`ip domain-name lab.local` #ciscoIOScommand
Задаёт domain name, который нужен, например, для генерации RSA keys при настройке SSH.

Где используется: на switch и router при secure remote access.

## 3. Команды для interfaces и IP

```bash
ip address 192.168.1.1 255.255.255.0
no shutdown
description Link to R1
ip default-gateway 192.168.1.254
```

`ip address 192.168.1.1 255.255.255.0` #ciscoIOScommand
Назначает IPv4 address интерфейсу.

Где используется: на router physical interface или на SVI коммутатора.

`no shutdown` #ciscoIOScommand
Включает interface administratively. Без этой команды port или interface может оставаться выключенным.

Где используется: очень часто на router interfaces и SVI. На switch access ports обычно и так активны, если их не выключали.

`description Link to R1` #ciscoIOScommand
Добавляет подпись к интерфейсу, чтобы было легче понимать назначение линка.

Где используется: на switch и router. Это не влияет на трафик, но сильно помогает в troubleshooting.

`ip default-gateway 192.168.1.254` #ciscoIOScommand
Задаёт default gateway для Layer 2 switch, чтобы им можно было управлять из другой сети.

Где используется: на L2 switch в global configuration mode.

> [!important] Важная логика
> `ip address` назначает адрес самому устройству или interface,  
> а `ip default-gateway` говорит, **куда отправлять трафик вне локальной сети**.

## 4. Команды для доступа к устройству

```bash
line console 0
password cisco
login
line vty 0 15
login local
transport input ssh
crypto key generate rsa
```

`password cisco` #ciscoIOScommand
Задаёт пароль для выбранной line, например console или VTY.

Где используется: внутри `line console 0` или `line vty 0 15`.

`login` #ciscoIOScommand
Говорит IOS реально запрашивать пароль на line. Если пароль есть, но нет `login`, защита не сработает как ожидается.

Где используется: в line configuration mode.

`login local` #ciscoIOScommand
Заставляет устройство использовать локальную базу пользователей, например `username admin secret ...`.

Где используется: обычно на VTY lines для SSH доступа.

`transport input ssh` #ciscoIOScommand
Разрешает вход на VTY lines только по SSH и отключает Telnet.

Где используется: на switch и router в line VTY configuration.

`crypto key generate rsa` #ciscoIOScommand
Генерирует RSA keys, без которых SSH на Cisco device обычно не заработает.

Где используется: на switch и router после задания `hostname` и `ip domain-name`.

> [!warning] Частая ошибка
> Для SSH одной команды `transport input ssh` недостаточно. Обычно ещё нужны:
> `hostname`, `ip domain-name`, `username ... secret ...`, `login local` и `crypto key generate rsa`.

## 5. Команды проверки

```bash
show running-config
show startup-config
show ip interface brief
show interfaces
show vlan brief
show mac address-table
show ip route
ping 192.168.1.1
copy running-config startup-config
```

`show running-config` #ciscoIOScommand
Показывает текущую активную конфигурацию, которая сейчас работает в RAM.

Где используется: на switch и router для проверки того, что реально настроено сейчас.

`show startup-config` #ciscoIOScommand
Показывает конфигурацию, сохранённую в NVRAM и используемую после перезагрузки.

Где используется: на switch и router, когда нужно сравнить сохранённую и текущую конфигурацию.

`show ip interface brief` #ciscoIOScommand
Быстро показывает interfaces, их IP addresses и status.

Где используется: одна из самых полезных verification commands на switch и router.

`show interfaces` #ciscoIOScommand
Показывает подробное состояние интерфейсов: speed, duplex, counters, errors и многое другое.

Где используется: при troubleshooting интерфейсов и линков.

`show vlan brief` #ciscoIOScommand
Показывает VLAN IDs, names и какие порты к ним относятся.

Где используется: на switch при проверке VLAN configuration.

`show mac address-table` #ciscoIOScommand
Показывает, какие MAC addresses switch выучил и на каких ports они находятся.

Где используется: на switch для понимания forwarding и поиска устройства по MAC.

`show ip route` #ciscoIOScommand
Показывает routing table устройства.

Где используется: в основном на router и Layer 3 switch.

`ping 192.168.1.1` #ciscoIOScommand
Проверяет reachability до другого устройства по IP.

Где используется: на switch и router для базовой проверки connectivity.

`copy running-config startup-config` #ciscoIOScommand
Сохраняет текущую running configuration в startup configuration.

Где используется: на switch и router после успешной настройки.

## Быстрая формула для запоминания

> [!tip] Memory Hook
> `enable -> configure terminal -> interface/line -> настройка -> show -> copy running-config startup-config`

## Если понял тему

> [!success] Итог
> Если ты понимаешь эту заметку, то умеешь:
> отличать mode в Cisco IOS,
> знать, где используется команда,
> базово настраивать switch или router,
> и проверять результат через `show` commands.

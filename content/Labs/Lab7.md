---
  protected: true
---

#labs

# Lab 7 — Port Security

> [!abstract] Суть лабы
> Настроить Port Security на 6 коммутаторах. Каждый коммутатор блокирует доступ к FTP серверу из-за неправильного MAC адреса. Нужно исправить конфиг, получить доступ к серверам через Telnet-цепочки и скачать FLAG. Максимум 100%.

## Source

https://drive.google.com/file/d/1LvF7eDPtS-9d316Phb6AGSIfNUGK_Es/view?usp=drivesdk

## Topic

- `Port Security (Static MAC, Sticky MAC)`
- `err-disabled recovery`
- `Telnet chains`
- `FTP access`

## Related Book Modules

- [[Book 2. Switching, Routing, and Wireless Essentials/10 - LAN Security Concepts/10 - LAN Security Concepts|Book 2 Module 10 — LAN Security Concepts]]
- [[Book 2. Switching, Routing, and Wireless Essentials/11 - Switch Security Configuration/11 - Switch Security Configuration|Book 2 Module 11 — Switch Security Configuration]]

## Цель

- Исправить Port Security на S1, S2, S3, S4/S5/S6 (Static или Sticky — зависит от ситуации)
- Получить доступ к FTP серверам 1stOctet, 2ndOctet, ThirdOctet, LastOctet через Telnet-цепочки
- Скачать FLAG с финального FTP сервера `114.31.56.127`

---

---

## Термины

**Port Security** — функция Cisco коммутатора, которая ограничивает доступ к порту по MAC адресу. Если подключается неизвестное устройство — порт уходит в err-disabled. #networkterm

**err-disabled** — состояние порта коммутатора после срабатывания Port Security или другого нарушения. Порт полностью отключается до ручного вмешательства. #networkterm

**sticky MAC** — режим Port Security при котором коммутатор автоматически запоминает MAC адрес первого подключённого устройства и сохраняет его в running-config. #networkterm

**static MAC** — режим Port Security при котором MAC адрес прописывается вручную администратором. #networkterm

**Telnet** — протокол удалённого управления устройствами по сети. Не шифрует трафик. #abbreviation

**FTP (File Transfer Protocol)** — протокол передачи файлов по сети. #abbreviation

**OSPF (Open Shortest Path First)** — динамический протокол маршрутизации. #abbreviation

**err-disabled recovery** — процесс восстановления порта из состояния err-disabled через `shutdown` / `no shutdown`. #networkterm

---

## Система оценивания

|Задача|Completion|Points|
|---|---|---|
|S1 configured correctly|11%|+11%|
|S2 configured correctly|22%|+11%|
|S3 configured correctly|33%|+11%|
|S4/S5/S6 (один из них)|44%|+11%|
|1stOctet FTP|55%|+11%|
|2ndOctet FTP|66%|+11%|
|ThirdOctet FTP|77%|+11%|
|LastOctet FTP|88%|+11%|
|FLAG retrieved|100%|+12%|

---

## Ключевое правило — Static vs Sticky

> [!important] Когда использовать Static, а когда Sticky?

|Ситуация|Метод|
|---|---|
|MAC адрес **известен** (виден в логах, `show arp`, `show mac-address-table`)|**Static:** `switchport port-security mac-address XXXX.XXXX.XXXX`|
|MAC адрес **неизвестен** (сервер заблокирован, недоступен)|**Sticky:** `switchport port-security mac-address sticky`|

> [!tip] Как найти MAC адрес `show port-security` → смотри поле **Last Source Address** — там будет MAC устройства которое пытается подключиться.

---

## Таблица IP адресов

|Устройство|IP Address|Сеть|Примечание|
|---|---|---|---|
|Laptop0|auto|10.0.1.0/24|Стартовая точка|
|R1|10.0.1.1|10.0.1.0/24|Gateway|
|S1|10.0.1.10|10.0.1.0/24||
|1stOctet|10.0.1.101|10.0.1.0/24|FTP сервер|
|R2|10.0.2.2 / 10.0.12.2 / 10.0.24.2|multiple||
|S3|10.0.2.30|10.0.2.0/24|В LAN R2!|
|ThirdOctet|10.0.2.100|10.0.2.0/24|FTP сервер|
|R3|10.0.3.3 / 10.0.13.3 / 10.0.23.3|multiple||
|S2|10.0.3.20|10.0.3.0/24|В LAN R3!|
|2ndOctet|10.0.3.100|10.0.3.0/24|FTP сервер|
|R4|10.0.4.4 / 10.0.24.4 / 192.168.1.4|multiple|Multilayer switch|
|S4|10.0.4.40|10.0.4.0/24||
|S5|10.0.4.50|10.0.4.0/24||
|S6|10.0.4.100|10.0.4.0/24||
|LastOctet|10.0.4.X|10.0.4.0/24|FTP сервер|
|ISP|192.168.1.1|192.168.1.0/24|Gateway to FLAG|
|FLAG server|114.31.56.127|за ISP|Финальная цель|

---

## Цепочки Telnet доступа

> [!warning] S2, S3, R3 — консоль заблокирована преподавателем! Доступ только через Telnet цепочки с Laptop0.

|Цель|Цепочка с Laptop0|
|---|---|
|R2|`telnet 10.0.12.2`|
|R3|`telnet 10.0.13.3`|
|S2|`telnet 10.0.3.20` (прямой!)|
|S3|`telnet 10.0.12.2` → `telnet 10.0.2.30`|
|R4|`telnet 10.0.12.2` → `telnet 10.0.24.4`|
|S4|`telnet 10.0.12.2` → `telnet 10.0.24.4` → `telnet 10.0.4.40`|
|S5|`telnet 10.0.12.2` → `telnet 10.0.24.4` → `telnet 10.0.4.50`|
|S6|`telnet 10.0.12.2` → `telnet 10.0.24.4` → `telnet 10.0.4.100`|

---

## Step 1 — Настройка S1 (→ 11%)

> [!note] Ситуация На S1 неправильный MAC на Fa0/1. MAC Laptop0 виден в логах нарушений.

### Сначала найди MAC Laptop0:

```
show port-security
```

`show port-security` #ciscoIOScommand Показывает статус Port Security на всех портах, включая **Last Source Address** — последний MAC который пытался подключиться.

### Fa0/1 — порт Laptop0 (MAC известен → static):

```
enable
configure terminal

interface fastEthernet 0/1
 shutdown
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address 00E0.8F8B.A56C
exit

end
write memory
```

### Fa0/2 — порт 1stOctet сервера (MAC неизвестен → sticky):

```
enable
configure terminal

interface fastEthernet 0/2
 shutdown
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address sticky
exit

end
write memory
```

`shutdown` / `no shutdown` #ciscoIOScommand Сброс порта из состояния err-disabled. `shutdown` выключает порт, `no shutdown` включает обратно — это очищает нарушение Port Security.

`no switchport port-security` #ciscoIOScommand Полностью удаляет все настройки Port Security с порта. Нужно перед перенастройкой чтобы избежать конфликтов.

`switchport port-security maximum 2` #ciscoIOScommand Устанавливает максимальное количество разрешённых MAC адресов на порту — 2.

`switchport port-security` #ciscoIOScommand Включает Port Security на порту. Без этой команды остальные port-security команды не активны.

`switchport port-security mac-address 00E0.8F8B.A56C` #ciscoIOScommand Статически прописывает разрешённый MAC адрес на порту.

`switchport port-security mac-address sticky` #ciscoIOScommand Включает sticky режим — коммутатор сам запомнит MAC первого подключённого устройства.

`write memory` #ciscoIOScommand Сохраняет running-config в startup-config. Без этого после перезагрузки конфиг потеряется.

> [!danger] Exam trap — порядок команд Сначала `maximum 2`, потом `mac-address`. Если сначала прописать MAC а потом maximum — получишь ошибку "maximum limit reached".

---

## Step 2 — Настройка S2 (→ 22%)

> [!note] Доступ через Telnet `telnet 10.0.3.20` — прямой доступ с Laptop0

### Fa0/1 — порт 2ndOctet сервера (MAC неизвестен → sticky):

```
telnet 10.0.3.20

enable
configure terminal

interface fastEthernet 0/1
 shutdown
 no switchport port-security mac-address 00E0.8FBB.A56C
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address sticky
exit

end
write memory
```

---

## Step 3 — Настройка S3 (→ 33%)

> [!warning] S3 находится в LAN R2, а не R3! Цепочка: `telnet 10.0.12.2` → `telnet 10.0.2.30`

### Fa0/1 — порт ThirdOctet сервера (MAC неизвестен → sticky):

```
telnet 10.0.12.2
telnet 10.0.2.30

enable
configure terminal

interface fastEthernet 0/1
 shutdown
 no switchport port-security mac-address 00E0.8FBB.A56C
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address sticky
exit

end
write memory
```

---

## Step 4 — Настройка R4 и S5 (→ 44%)

> [!important] Сначала OSPF на R4! Без OSPF Laptop0 не может достучаться до сети 10.0.4.0/24.

### Доступ к R4:

```
telnet 10.0.12.2
telnet 10.0.24.4
```

### R4 — добавить OSPF:

```
enable
configure terminal

router ospf 1
 network 10.0.4.0 0.0.0.255 area 0
 network 10.0.24.0 0.0.0.255 area 0
 default-information originate
exit
```

`router ospf 1` #ciscoIOScommand Включает процесс OSPF с ID 1 на устройстве.

`network 10.0.4.0 0.0.0.255 area 0` #ciscoIOScommand Добавляет сеть 10.0.4.0/24 в OSPF area 0. Wildcard маска `0.0.0.255` = инверсия маски /24.

`default-information originate` #ciscoIOScommand Распространяет маршрут по умолчанию через OSPF на соседей.

### S5 — Fix Fa0/1 (MAC известен → static):

```
telnet 10.0.4.50

enable
configure terminal

interface fastEthernet 0/1
 shutdown
 no switchport port-security
 no shutdown
 switchport mode access
 switchport port-security maximum 2
 switchport port-security
 switchport port-security mac-address 0010.1103.0741
exit

end
write memory
```

> [!note] S4 и S6 S4 и S6 могут быть недоступны по Telnet. Настройки S5 достаточно для получения 44%.

---

## Steps 5–8 — FTP серверы (55% → 88%)

> [!tip] Credentials для всех FTP серверов username: **cisco** / password: **cisco**

### 1stOctet (→ 55%):

```
ftp 10.0.1.101
```

Значение октета: **114**

### 2ndOctet (→ 66%):

```
ftp 10.0.3.100
```

Значение октета: **31**

### ThirdOctet (→ 77%):

```
ftp 10.0.2.100
```

Значение октета: **56**

### LastOctet (→ 88%):

Сначала найди IP через `show arp` на R4:

```
telnet 10.0.12.2
telnet 10.0.24.4
show arp
ftp [LastOctet IP]
```

`show arp` #ciscoIOScommand Показывает ARP таблицу роутера — все IP и соответствующие MAC адреса в подключённых сетях. Используй чтобы найти IP LastOctet сервера.

Значение октета: **127**

---

## Step 9 — FLAG (→ 100%)

### Собери IP из октетов:

|1st Octet|2nd Octet|3rd Octet|Last Octet|
|---|---|---|---|
|114|31|56|127|

**FLAG Server IP: `114.31.56.127`**

### Подключись и забери FLAG:

```
ftp 114.31.56.127
dir
get FLAG
```

`dir` #ciscoIOScommand Показывает список файлов на FTP сервере.

`get FLAG` #ciscoIOScommand Скачивает файл FLAG с FTP сервера.

> [!success] FLAG `INF_311{TH3_P0RT_63CUR1T9_16_C00L}`

---

## Troubleshooting

> [!warning] Оранжевый порт в Packet Tracer Оранжевый цвет = **err-disabled**. Port Security сработал и отключил порт. Исправление: `shutdown` → `no shutdown` после перенастройки.

> [!tip] Узнать свой IP адрес на устройстве `ping 0.0.0.0` — на любом устройстве покажет его собственный IP адрес.

> [!danger] R4 — Multilayer Switch R4 является L3 свичом. Перед командами port-security нужно сначала написать `switchport` на интерфейсе — иначе порт в routed mode и port-security не применится.

> [!warning] Порядок команд Port Security Всегда: `maximum 2` → потом `mac-address`. Иначе ошибка "maximum limit reached".

> [!note] S3 в LAN R2, не R3! Частая ошибка — искать S3 через R3. S3 (10.0.2.30) находится в сети 10.0.2.0/24 которая принадлежит R2.


> [!tip] Memory Hook
> ARP = "Кто владеет этим IP?" Broadcast запрос → unicast ответ → запись в ARP table.

> [!important] Layer 2 vs Layer 3
> Switch работает с MAC адресами (Layer 2). Router работает с IP адресами (Layer 3).
> ARP — мост между ними: переводит IP → MAC.

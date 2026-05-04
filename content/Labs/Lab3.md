---
  protected: true
---

#labs

# Lab 3 — Application Layer

> [!abstract] Суть лабы
> Проверить работу сервисов Application Layer: DNS, HTTP/HTTPS, FTP, Email (SMTP/POP3), DHCP. Настройка идёт не командами IOS, а через GUI Packet Tracer — роутеры и свитчи уже преднастроены.

## Source

https://drive.google.com/file/d/1IkXnHIf6A5oZ4qN_I7rBFAjDkyrT50/view?usp=drivesdk

## Topic

- `DNS (Domain Name System)`
- `HTTP / HTTPS`
- `FTP / TFTP`
- `SMTP / POP3 (Email)`
- `DHCP`

## Related Book Modules

- [[Book 1. Introduction to Networks/15 - Application Layer/15 - Application Layer|Book 1 Module 15 — Application Layer]]

## Цель

- Проверить DNS resolution (ping по имени, nslookup)
- Открыть web-страницу через HTTP/HTTPS
- Передать файл через FTP
- Отправить и получить email через SMTP/POP3
- Проверить DHCP выдачу адреса

---

## Термины

**DNS (Domain Name System)** — система перевода доменных имён в IP адреса. Без DNS нельзя пинговать `google.com`. #abbreviation

**HTTP (HyperText Transfer Protocol)** — протокол передачи веб-страниц. Port 80. #abbreviation

**HTTPS** — HTTP с шифрованием TLS/SSL. Port 443. #abbreviation

**FTP (File Transfer Protocol)** — протокол передачи файлов. Port 21 (control), Port 20 (data). #abbreviation

**SMTP (Simple Mail Transfer Protocol)** — протокол отправки email. Port 25. #abbreviation

**POP3 (Post Office Protocol 3)** — протокол получения email с сервера. Port 110. #abbreviation

**DHCP (Dynamic Host Configuration Protocol)** — автоматическая выдача IP адреса, маски, шлюза и DNS. #abbreviation

---

## Решение

> [!important] Важно
> В этой лабе настройка идёт через GUI Packet Tracer, не через CLI. Открывай устройства → вкладка Desktop.

### Проверка DNS и HTTP

1. Открой PC → Desktop → Web Browser
2. Введи URL сервера (например `http://webserver.com`)
3. Если страница открылась — HTTP и DNS работают

### Проверка FTP

1. Открой PC → Desktop → Command Prompt
2. Введи:
```
ftp [IP или hostname FTP сервера]
```
3. Введи username и password (обычно `cisco` / `cisco`)
4. Команды внутри FTP:
```
dir          — список файлов
get file.txt — скачать файл
put file.txt — загрузить файл
quit         — выйти
```

### Проверка Email

1. Открой PC → Desktop → Email
2. Настрой SMTP и POP3 сервер (адрес email сервера)
3. Отправь письмо → проверь что дошло

### Проверка DHCP

1. Открой PC → Desktop → IP Configuration
2. Выбери **DHCP** (не Static)
3. Подожди — PC должен получить IP автоматически

### Команды в Command Prompt на PC

```
ipconfig /all          — показать IP, маску, шлюз, DNS
ping hostname          — проверить DNS resolution
nslookup hostname      — запросить DNS запись вручную
```

`ipconfig /all` Показывает полную IP конфигурацию включая MAC адрес, DNS сервер, DHCP статус.

`nslookup hostname` Напрямую запрашивает DNS сервер. Полезно когда ping не работает — можно понять, DNS виноват или маршрутизация.

> [!tip] Memory Hook
> Layer 7 = то что видит пользователь. DNS → HTTP → FTP → Email → DHCP. Всё это Application Layer.

> [!important] Порядок проверки
> 1. Сначала проверь IP (ipconfig) — есть ли адрес?
> 2. Потом DNS (nslookup) — резолвится ли имя?
> 3. Потом HTTP (браузер) — открывается ли страница?

> [!warning] Частая ошибка
> Если ping по IP проходит, а ping по имени нет — проблема в DNS, не в маршрутизации.

---

> [!success] Итог
> Если понял лабу — знаешь разницу между протоколами Application Layer, умеешь проверять работу DNS, HTTP, FTP, Email и DHCP через Packet Tracer.

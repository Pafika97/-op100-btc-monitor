# Пошаговая инструкция — Bitcoin Top‑100 Holders Monitor

Файл: `TOP100_BTC_MONITOR_INSTRUCTIONS.md`

Ниже — подробная пошаговая инструкция по установке, настройке и запуску монитора топ‑100 холдеров BTC с отправкой уведомлений в Telegram. Все действия делайте в терминале/PowerShell в каталоге, куда вы распаковали архив `top100_btc_monitor.zip`.

---
## 1) Требования
- Python 3.10 или новее
- Доступ в интернет
- Установленные pip и virtualenv (рекомендуется)
- Telegram‑бот (получить токен у @BotFather)
- Chat ID (идентификатор чата или канала, в который бот будет отправлять сообщения)

---
## 2) Подготовка окружения (Linux/macOS)
1. Откройте терминал и перейдите в папку проекта:
   ```bash
   cd /путь/к/распакованной/папке/top100_btc_monitor
   ```
2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   На Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

---
## 3) Настройка Telegram бота
1. Создайте бота через @BotFather в Telegram и получите `BOT_TOKEN` (формат: `123456:ABC-...`).
2. Добавьте бота в нужный чат или канал и сделайте его администратором (если отправляете в канал).
3. Узнайте `CHAT_ID`:
   - Для личного чата: используйте @userinfobot или отправьте сообщение и посмотрите ID.
   - Для группы: добавьте бота в группу, затем используйте @getidsbot или ваш код для получения `chat_id` (обычно отрицательное число для супергрупп).

---
## 4) Создание конфигурационного файла
1. Скопируйте пример конфига:
   ```bash
   cp config.example.yaml config.yaml
   ```
2. Откройте `config.yaml` в любом текстовом редакторе и заполните поля:
   ```yaml
   telegram_bot_token: "ВАШ_BOT_TOKEN"
   telegram_chat_id: ВАШ_CHAT_ID    # число, без кавычек
   poll_interval_seconds: 300      # частота опроса в секундах
   source: "bitinfocharts"         # или "blockchair"
   blockchair_api_key: ""          # опционально
   ```
3. Сохраните файл.

---
## 5) Первый запуск (ручной)
Запустите монитор:
```bash
python main.py
```
- При первом запуске будет создана база `monitor.db` (файл в папке проекта).
- Если конфиг заполнен верно, вы увидите логи и, при первом обнаружении разницы, сообщение в Telegram.

---
## 6) Частые ошибки и отладка
- `Config file not found` — убедитесь, что `config.yaml` в текущей директории.
- Ошибка при отправке в Telegram — проверьте `telegram_bot_token` и `chat_id`, и убедитесь, что бот добавлен в чат.
- Scraping bitinfocharts не находит таблицу — сайт изменил HTML. В этом случае используйте `source: "blockchair"` (если есть API‑ключ) или сообщите мне — я поправлю парсер.
- Timeout/Network errors — проверьте подключение, возможно нужен прокси или увеличение таймаутов в `helpers.py`.

---
## 7) Рекомендации по продакшн‑запуску
### Вариант A — systemd (Linux)
1. Создайте systemd unit `/etc/systemd/system/top100-monitor.service`:
   ```ini
   [Unit]
   Description=Top100 BTC Monitor
   After=network.target

   [Service]
   User=ваш_пользователь
   WorkingDirectory=/путь/к/top100_btc_monitor
   ExecStart=/путь/к/top100_btc_monitor/venv/bin/python main.py
   Restart=on-failure
   RestartSec=10s

   [Install]
   WantedBy=multi-user.target
   ```
2. Перезагрузите systemd и включите сервис:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now top100-monitor.service
   ```

### Вариант B — Docker (быстро воспроизводимо)
1. Пример Dockerfile можно сделать — напишите, если нужно, и я подготовлю.
2. Запустите контейнер в background и подключите volume для сохранения `monitor.db` и `config.yaml`.

---
## 8) Улучшения (по желанию)
- Подключить Blockchair с API‑ключом (надежнее, чем скрапинг).
- Подключить таблицу известных меток (labels) — пометить адреса бирж/пулы с помощью публичных баз (walletexplorer, Blockchair labels).
- Добавить кластеризацию (объединять адреса в сущности).
- Добавить фильтры оповещений: только новые адреса, только ушедшие, только баланс > X BTC.
- Форматировать сообщения в Telegram (Markdown) и отправлять краткие дайджесты (например, топ10 изменений за 1 час).

---
## 9) Полезные команды
- Просмотреть логи systemd:
  ```bash
  sudo journalctl -u top100-monitor.service -f
  ```
- Остановить/запустить сервис:
  ```bash
  sudo systemctl stop top100-monitor.service
  sudo systemctl start top100-monitor.service
  ```

---
## 10) Если нужно — я помогу
Могу дополнительно:
- Подготовить Dockerfile + docker-compose.yml
- Добавить systemd unit, настроенный под ваш путь/пользователя
- Реализовать Blockchair flow и примеры форматированных Telegram‑уведомлений
- Добавить скрипт для получения chat_id автоматически

Сообщите, какой вариант вы хотите — Docker / systemd / только локально — и я подготовлю соответствующий файл.

---
Сохраню эту инструкцию в файл `TOP100_BTC_MONITOR_INSTRUCTIONS.md` в /mnt/data

# WorldTravel WhatsApp Bot 🌍

Telegram-style WhatsApp бот для туристического агентства WorldTravel (Бишкек).  
**Stack:** Python 3 · Flask · Groq (Llama 3.1) · Evolution API · MySQL · Railway

---

## Деплой на Railway — пошаговая инструкция

### 1. Создание аккаунта и проекта

1. Зайди на [railway.app](https://railway.app) и войди через GitHub
2. Нажми **New Project → Deploy from GitHub repo**
3. Выбери репозиторий `Morpheus00072/itshop-bot-main`
4. Railway автоматически определит Python-проект и начнёт сборку

### 2. Добавление MySQL базы данных

1. В проекте нажми **+ New** → **Database** → **MySQL**
2. Railway создаст базу и автоматически добавит переменные:
   - `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`
3. Открой Shell базы данных и выполни SQL из `shop_db_export.sql`:
   ```
   Откройте MySQL Shell → скопируйте и вставьте содержимое shop_db_export.sql
   ```

### 3. Настройка переменных окружения

В Railway → Settings → Variables добавь:

| Переменная | Значение |
|---|---|
| `GROQ_KEY` | Ключ с [console.groq.com](https://console.groq.com) |
| `EVOLUTION_URL` | URL вашего Evolution API сервера |
| `EVOLUTION_API_KEY` | API ключ Evolution |
| `EVOLUTION_INSTANCE` | Название инстанса |
| `BOSS_NUMBER` | Номер менеджера (без +), напр. `996755212525` |
| `BOT_PHONE` | Номер WhatsApp бота, напр. `996220891639` |
| `MBANK_QR_URL` | Ссылка на QR-код для оплаты |

### 4. Получение Groq API ключа

1. Зайди на [console.groq.com](https://console.groq.com)
2. Создай аккаунт → **API Keys** → **Create API Key**
3. Скопируй ключ (начинается с `gsk_...`) и вставь в Railway

### 5. Настройка Evolution API и получение QR

1. Разверни [Evolution API](https://github.com/EvolutionAPI/evolution-api) на отдельном сервере
2. Создай инстанс через API или Dashboard
3. Для получения QR-кода:
   ```
   GET {EVOLUTION_URL}/instance/connect/{INSTANCE_NAME}
   Headers: apikey: {EVOLUTION_API_KEY}
   ```
4. Отсканируй QR в WhatsApp → три точки → **Связанные устройства** → **Привязать устройство**

### 6. Настройка Webhook

После деплоя Railway даст URL вида `https://xxx.railway.app`.  
Настрой webhook в Evolution API:
```
POST {EVOLUTION_URL}/webhook/set/{INSTANCE_NAME}
{
  "url": "https://xxx.railway.app/webhook",
  "webhook_by_events": false,
  "events": ["MESSAGES_UPSERT"]
}
```

### 7. Проверка

- `GET https://xxx.railway.app/status` — должен вернуть статус бота
- `GET https://xxx.railway.app/` — веб-интерфейс бота

---

## Команды для менеджера (WhatsApp)

| Команда | Описание |
|---|---|
| `статистика` | Число клиентов, туров, ожидающих заявок |
| `рассылка Текст...` | Отправить сообщение всем клиентам |
| `написать 996XXX текст` | Написать конкретному клиенту |
| `добавить тур [данные]` | Добавить тур в каталог |
| `убрать тур [название]` | Скрыть тур |
| `цена [название] [сумма]` | Изменить цену тура |
| `да` | Подтвердить первую заявку в очереди |
| `да {ID}` | Подтвердить конкретную заявку по ID |
| `нет` | Отклонить первую заявку |
| `заявки` | Показать все ожидающие заявки |
| `история` | История переписок |
| `пауза` / `запустить` | Остановить/запустить бота |
| `разблокировать 996XXX` | Снять rate-limit с клиента |
| `помощь` | Показать все команды |

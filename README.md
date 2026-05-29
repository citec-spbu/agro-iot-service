# agro-iot-service

IoT-приёмник датчиков и метеостанций для платформы **Agro Digital Twin**: TCP-сервер для бинарных пакетов с устройств + REST API для регистрации, истории, агрегатов и дашбордов.

## Возможности

- TCP-сервер на порту **9000** (бинарный протокол, FK-валидация по серийнику).
- REST API под `/api/iot/*`: регистрация, текущие значения, история, агрегаты, дашборд.
- Координаты станций + опц. point-in-polygon проверка по контурам поля через `fields-service`.
- JWT-авторизация через `auth-service`/`api-gateway` (`auth_request introspect`).

## Стек

Python 3.11
FastAPI
SQLAlchemy 2 async
asyncpg
Alembic
Postgres 15
shapely
httpx

## Схема БД

```
stations
  field_id      UUID  PK            -- бизнес-id поля (в текущей модели одна станция = одно поле)
  hardware_id   BIGINT UNIQUE       -- айди станции из пакета
  org_id        UUID  NOT NULL  INDEXED
  name          TEXT
  latitude      DOUBLE PRECISION
  longitude     DOUBLE PRECISION
  polling_interval DOUBLE PRECISION DEFAULT 0.5 -- интервал опроса датчиков станцией, в минутах
  last_seen_at  TIMESTAMP           -- в TZ из APP_TZ_NAME

station_data                          -- ON DELETE CASCADE от stations
  id        UUID PK
  field_id  UUID NOT NULL FK -> stations.field_id
  payload   JSONB
  date_time TIMESTAMP

sensor_data                           -- ON DELETE CASCADE от stations
  id        UUID PK
  field_id  UUID NOT NULL FK -> stations.field_id
  sensor_id INTEGER NOT NULL          -- ID датчика из пакета
  payload   JSONB
  date_time TIMESTAMP
```

## TCP-протокол

Незарегистрированные `hardware_id` отбрасываются (warning в лог).

**Station** (`0x01`):
```
[0xAA][0x01][hardware_id 8B][len 2B][payload]
payload = { param_id 1B, value Nb }*
Station payload включает температуру и влажность станции (`soil_moisture`), а также ветер и осадки.
params:
  0x00 temperature (2B)    -> (raw - 900) / 10
  0x01 soil_moisture (1B)  -> raw %
  0x02 wind_speed (2B)     -> (((high - 1) << 8) + low - 1) / 5
  0x03 wind_direction (2B) -> ((high - 1) << 8) + low - 1
  0x04 rain (2B)           -> (((high - 1) << 8) + low - 1) / 5
```

**Sensor** (`0x02`):
```
[0xAA][0x02][hardware_id 8B][sensor_id 4B][len 2B][payload]
params:
  0x00 soil_moisturea (1B) -> raw %
  0x01 temperaturea (1B)   -> -20 + raw * 80 / 255
  0x02 soil_moisturez (1B) -> raw %
  0x03 temperaturez (1B)   -> -55 + raw * 180 / 255
```

## API

Все маршруты под `/api/iot`, авторизация `Authorization: Bearer <jwt>`. История ASC по `date_time`, границы `date_from`/`date_to` включительные. Время — naive в TZ из `APP_TZ_NAME` (default `Europe/Moscow`).

### Управление станциями (по `field_id`)

| Method | Path | Описание |
|---|---|---|
| POST | `/stations` | Регистрация (`field_id`, `hardware_id`, `name?`, `latitude?`, `longitude?`, `polling_interval?`; по умолчанию `0.5` минуты) |
| GET | `/stations` | Мои станции |
| GET / PUT / DELETE | `/stations/{field_id}` | Чтение / обновление (`name`/`lat`/`lon`/`polling_interval`) / удаление (CASCADE) |

### Данные (по `field_id`)

| Method | Path | Описание |
|---|---|---|
| GET | `/fields/{field_id}/stations` | Станции на поле + `online` + `last_seen_at` + `polling_interval` (для карты) |
| GET | `/fields/{field_id}/data/last` | Последний пакет станции |
| GET | `/fields/{field_id}/data/history?date_from=&date_to=` | История пакетов |
| GET | `/fields/{field_id}/data/summary?date_from=&date_to=` | avg/min/max по каждому ключу payload |
| GET | `/fields/{field_id}/sensors` | Список `sensor_id` |
| GET | `/fields/{field_id}/sensors/{sid}/data/{last,history,summary}` | Аналогично, по конкретному датчику |
| GET | `/dashboard` | Все станции org + `online` + `last_data` + sensors с `last_data` (один запрос для главной) |

## Запуск

```bash
docker network create agronetwork    # один раз
cp .env.example .env
docker compose up -d
```
- Swagger: <http://localhost:8006/docs>
- TCP из Docker-контейнера: внутренний порт `9000`; с хоста по текущему `docker-compose.yml`: `localhost:9006` (`9006:9000`).

## Интеграция с платформой

- `auth-service` — JWT introspect (`APP_AUTH_SERVICE_URL`).
- `api-gateway` — нужна `location /api/iot { auth_request /api/auth/introspect; proxy_pass http://iot-service:8080/api/iot; }`.
- `fields-service` — опц. при регистрации (через gateway, JWT пробрасывается).

## Пути дальнейшего развития

- Сейчас станция привязывается к `field_id`, то есть к полю целиком. Если понадобится учитывать размещение станции внутри конкретного контура, можно расширить модель до связи с `contour_id` и обновить фронт.

- Возможна замена TCP-контура приёма данных на MQTT-брокер с последующим обновлением прошивки станции.

- Уже поддержано хранение интервала опроса датчиков станцией в `stations.polling_interval` в минутах. Следующий шаг — определить механизм передачи этого значения на станцию и применить его в логике опроса датчиков.

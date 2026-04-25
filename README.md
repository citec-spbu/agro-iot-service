# agro-iot-service

IoT-приёмник датчиков и метеостанций для платформы **Agro Digital Twin**: TCP-сервер для бинарных пакетов с устройств + REST API для регистрации и дашбордов.

## Возможности

- TCP-сервер на порту **9000** — бинарный протокол, FK-валидация по серийнику.
- REST API под `/api/iot/*` — регистрация станций, текущие значения, история.
- Координаты станций + опц. проверка попадания в контур поля (`fields-service`).
- JWT-авторизация через `auth-service`/`api-gateway` (`auth_request introspect`).

## Стек

Python 3.11 · FastAPI · SQLAlchemy 2 async · asyncpg · Alembic · Postgres 15 · shapely · httpx.

## Запуск

```bash
docker network create agronetwork    # один раз
cp .env.example .env
docker compose up -d
```

- API + Swagger: <http://localhost:8006/docs>
- TCP: `localhost:9000`

## API

Все маршруты под `/api/iot`, авторизация `Authorization: Bearer <jwt>`.

| Method | Path | Описание |
|---|---|---|
| POST | `/stations` | Регистрация (`hardware_id`, `field_id`, опц. `name`, `latitude`, `longitude`) |
| GET | `/stations` | Мои станции |
| GET / PUT / DELETE | `/stations/{hardware_id}` | Чтение / обновление / удаление |
| GET | `/fields/{field_id}/stations` | Станции на поле + `online` + `last_seen_at` |
| GET | `/stations/{hardware_id}/sensors` | `sensor_id`-ы для станции |
| GET | `/stations/{hardware_id}/data/last` | Последний пакет станции |
| GET | `/stations/{hardware_id}/data/history?date_from=&date_to=` | История |
| GET | `/stations/{hardware_id}/sensors/{sensor_id}/data/{last,history}` | Последний пакет / история датчика |

## TCP-протокол

Big-endian. Незарегистрированные `hardware_id` отбрасываются (FK + warning).

**Station** (`0x01`):
```
[0xAA][0x01][hardware_id 8B][len 2B][payload]
payload = { param_id 1B, value Nb }*
params: 0x00 wind_speed (2B) | 0x01 wind_direction (2B) | 0x02 rain (2B)
```

**Sensor** (`0x02`):
```
[0xAA][0x02][hardware_id 8B][sensor_id 4B][len 2B][payload]
params: 0x00 temperature (2B) | 0x01 soil_moisture (1B)
```

## Схема БД

```
stations(hardware_id BIGINT PK, field_id UUID UNIQUE, org_id UUID,
         name, latitude, longitude, last_seen_at)
station_data(id UUID PK, station_id BIGINT FK ON DELETE CASCADE,
             payload JSONB, date_time)
sensor_data(id UUID PK, station_id BIGINT FK ON DELETE CASCADE,
            sensor_id INTEGER, payload JSONB, date_time)
```

## Интеграция с платформой

- `auth-service` — JWT introspect (`APP_AUTH_SERVICE_URL`).
- `api-gateway` — нужна `location /api/iot { auth_request /api/auth/introspect; proxy_pass http://iot-service:8080/api/iot; }`.
- `fields-service` — опц. для point-in-polygon при регистрации (через gateway, JWT пробрасывается).

Сервис работает **параллельно** с OpenMeteo-`meteo-service`, не заменяя его.

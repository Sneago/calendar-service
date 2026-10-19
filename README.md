# Calendar Service

Аналог гугл-календаря: разовые и повторяющиеся события, отмена и переименование одного вхождения, удаление серии начиная с выбранного вхождения. Django + DRF + PostgreSQL.

## Запуск в Docker

```bash
cp .env.example .env
docker compose up --build
```

Сервис слушает http://localhost:8000, Swagger: http://localhost:8000/api/docs/

## API

| Запрос | Что делает | Ответ |
|---|---|---|
| `POST /add/` | создать событие `{"name", "start_at", "period"}` | 201 `{"id"}` |
| `POST /remove/{id}/{year}/{month}/{day}/` | удалить событие | 204; 404, если события нет |
| `POST /remove-next/{id}/{year}/{month}/{day}/` | удалить событие и последующие | 204; 404, если события нет |
| `POST /update/{id}/{year}/{month}/{day}/` | переименовать событие `{"name"}` | 200 `{"id", "name"}`; 404, если события нет |
| `GET /events/{year}/{month}/{day}/` | события дня, по времени начала | 200 `[{"id", "name"}]`; 404 на несуществующую дату вроде `2026/2/30` |

`start_at` — unix timestamp в секундах (UTC), `period` — шаг повтора в днях или `null` для разового события. Дата в URL — день по UTC, `id` — id серии, общий у всех её событий.

## Сценарий проверки

Еженедельная планёрка со среды 2 января 2030, 09:00 UTC. На чистой базе её id равен 1; если база не пустая, подставьте id из ответа `add`.

```bash
curl -X POST http://localhost:8000/add/ -H 'Content-Type: application/json' -d '{"name": "Планёрка", "start_at": 1893574800, "period": 7}'
# {"id":1}

curl http://localhost:8000/events/2030/1/2/   # [{"id":1,"name":"Планёрка"}]
curl http://localhost:8000/events/2030/1/3/   # []
curl http://localhost:8000/events/2030/1/9/   # [{"id":1,"name":"Планёрка"}]
curl http://localhost:8000/events/2030/1/16/  # [{"id":1,"name":"Планёрка"}]
```

Переименовать вхождение 9 января (день 7):

```bash
curl -X POST http://localhost:8000/update/1/2030/1/9/ -H 'Content-Type: application/json' -d '{"name": "Ретро"}'
# {"id":1,"name":"Ретро"}

curl http://localhost:8000/events/2030/1/9/   # [{"id":1,"name":"Ретро"}]
curl http://localhost:8000/events/2030/1/16/  # [{"id":1,"name":"Планёрка"}]
```

Удалить вхождение 16 января (день 14):

```bash
curl -X POST http://localhost:8000/remove/1/2030/1/16/   # 204, пустое тело

curl http://localhost:8000/events/2030/1/16/  # []
curl http://localhost:8000/events/2030/1/23/  # [{"id":1,"name":"Планёрка"}]
```

Удалить серию начиная с 23 января (день 21):

```bash
curl -X POST http://localhost:8000/remove-next/1/2030/1/23/   # 204, пустое тело

curl http://localhost:8000/events/2030/1/23/  # []
curl http://localhost:8000/events/2030/1/30/  # []
curl http://localhost:8000/events/2030/1/2/   # [{"id":1,"name":"Планёрка"}]
curl http://localhost:8000/events/2030/1/9/   # [{"id":1,"name":"Ретро"}]
```

Повтор уже выполненной операции:

```bash
curl -X POST http://localhost:8000/remove/1/2030/1/16/        # 404 {"detail":"Not found."}
curl -X POST http://localhost:8000/remove-next/1/2030/1/23/   # 404 {"detail":"Not found."}
```

## Архитектурные решения

- Единичные записи о серии событий вместо записи каждого отдельно. В `Event` — начало `start_at`, периодичность `period` и дата окончания `until`; новое имя или отмена конкретного события — строка `OccurrenceOverride` (`date`, `name`, `is_cancelled`).
- Есть ли событие в этот день, решает один запрос — `EventQuerySet.occurring_on(day)`: по `start_at`, `period`, `until` и override этого дня. Его используют и список `events`, и проверка перед `remove`/`update`/`remove-next`, поэтому список и 404 не расходятся.
- Изменения одной серии выполняются по очереди: `remove`, `update` и `remove-next` сначала блокируют строку `Event`, а потом отдельным запросом проверяют, есть ли событие в этот день. Иначе два одновременных `remove` одного события оба ответили бы 204.
- На `start_at` два отдельных индекса, для разовых событий и для серий. Разовые события дня находятся по индексу сразу, а серии перебираются только те что начались не позже этого дня, поэтому время ответа `events` зависит от числа серий, а не от того, сколько у них событий.
- Ограничения `period >= 1` и `start_at >= 0` проверяет сама база, а не только сериализатор, который можно обойти через `bulk_create`, `update()` или сырой SQL. Одна серия с `period = 0` сломала бы `events` для всех: при расчёте событий дня получилось бы деление на ноль.

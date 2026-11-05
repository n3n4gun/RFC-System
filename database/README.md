# Инициализация PostgreSQL

`init/001_create_tables.sql` создаёт таблицы `users_table`, `active_users`
и `applications_table` по текущим моделям и запросам приложения.
Пароль пользователя хранится как хеш, поэтому колонка `password` имеет тип TEXT.
ID хранятся как VARCHAR(32), чтобы сохранить строковый формат `uuid.uuid4().hex`
и совместимость с текущей авторизацией. Время хранится без часового пояса,
согласно текущему использованию `datetime.now().isoformat()`.

Сервис PostgreSQL `compose.yaml` в корне проекта:

```yaml
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: ${DB_NAME:?Set DB_NAME}
      POSTGRES_USER: ${DB_USER:?Set DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD:?Set DB_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro

volumes:
  postgres_data:
```

Переменные `DB_NAME`, `DB_USER`, `DB_PASSWORD` задаются в корневом `.env`.
Саму базу создаёт entrypoint образа по `POSTGRES_DB`; SQL-скрипт создаёт
таблицы внутри неё, поэтому `CREATE DATABASE` в нём не нужен.

Для приложения, запущенного на хосте, укажи `DB_HOST=localhost`, `DB_PORT=5432`.
Для приложения в той же сети Compose используй `DB_HOST=db`, `DB_PORT=5432`.

Скрипты из `/docker-entrypoint-initdb.d` выполняются только при первой
инициализации пустого каталога данных. Перезапуск контейнера с существующим
томом не применяет изменения SQL. Для дальнейшего изменения схемы нужны
миграции; этот скрипт предназначен для новой базы.

Документация образа: https://hub.docker.com/_/postgres

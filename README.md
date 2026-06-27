# The Wall — backend

Микросервисная платформа публикации сообщений: автоматическая модерация,
дедупликация и полнотекстовый поиск. Два FastAPI-сервиса поверх **общей
PostgreSQL** (точка интеграции — таблица `messages`).

- **message_service** (`:8002`) — путь записи: публикация, модерация, дедуп, видимость.
- **search_service** (`:8003`) — путь чтения: полнотекстовый поиск (PostgreSQL FTS).

## Структура

```
services/
  message_service/            # запись (:8002)
    api/                      # router (/messages/*), Pydantic-схемы
    application/              # use-cases: publish, visibility (hide/detach/erase)
    domain/                   # сущность Message, правила, исключения
    infrastructure/           # db_models, repositories, message_index (NullIndexer — заглушка)
    moderation_module/        # pipeline + steps (ban_words, pii, ...)
  search_service/             # чтение (:8003)
    api/                      # router (/search/messages), схемы ответа
    application/              # classic_search (FTS); fulltext/semantic — заглушки
    domain/                   # SearchQuery, SearchResult, SearchResponse
    infrastructure/           # message_search_repo (FTS), search_log_repo
libs/                         # общий код
  postgres/                   # async engine, session, Base
  fastapi/                    # app_factory, обработчики ошибок, зависимости
  ai/ , qdrant/               # embeddings/Qdrant — заглушки (вектор вне scope)
  config_loader.py , logging/
tests/                        # unit (domain, moderation, repos, libs) + integration
docker-compose.yml            # PostgreSQL 16 на хост-порту 5433
migrations/                   # каркас Alembic (WIP)
```

## Запуск

Требуется Python 3.10+, [Poetry](https://python-poetry.org/) и Docker.

```bash
# 1. поднять PostgreSQL
docker compose up -d

# 2. установить зависимости
poetry install

# 3. прогнать тесты (integration требует поднятой БД из шага 1)
poetry run pytest

# 4. запустить сервисы (каждый в своём терминале)
poetry run python -m services.message_service.main   # http://localhost:8002/docs
poetry run python -m services.search_service.main    # http://localhost:8003/docs
```

Подключение к БД берётся из `DATABASE_URL` (по умолчанию — Postgres из
`docker-compose`, порт 5433); переменные см. в [.env.example](.env.example).

> ⚠️ Схема БД сейчас создаётся фикстурами интеграционных тестов (`Base.metadata.create_all`).
> Alembic-миграции для standalone-запуска сервисов пока в разработке.

## Эндпоинты

**message_service (`:8002`)**

| Метод | Путь                    | Назначение                                            |
|-------|-------------------------|-------------------------------------------------------|
| POST  | `/messages/publish`     | публикация (`201`; `409` дубль; `422` hard-модерация) |
| POST  | `/messages/{id}/hide`   | скрыть из выдачи                                      |
| POST  | `/messages/{id}/detach` | убрать авторство                                      |
| POST  | `/messages/{id}/erase`  | hide + detach                                         |

**search_service (`:8003`)**

| Метод | Путь                                | Назначение                                      |
|-------|-------------------------------------|-------------------------------------------------|
| GET   | `/search/messages?query_string=...` | FTS-поиск (`400` пустой/слишком длинный запрос) |

## Реализованные сценарии

Покрыто интеграционными тестами ([tests/test_message_search_integration.py](tests/test_message_search_integration.py)):

- **Публикация → поиск**: опубликованное сообщение находится по FTS (id, snippet, rank).
- **Многоязычность**: поиск работает для любого языка (конфигурация `simple`, без стемминга — EN/RU/DE).
- **Ранжирование**: результаты сортируются по `rank`, корректный `total_count`.
- **Жёсткая модерация**: запрещённый контент → `422`, в поиск не попадает.
- **Мягкая модерация**: предупреждения (напр. PII) → публикуется и ищется.
- **Дедупликация**: повторный текст → `409`.
- **Видимость**: `hide`/`erase` убирают сообщение из выдачи; `erase` снимает авторство.
- **Логирование поиска**: каждый запрос пишется в `search_log`.
- **Валидация запроса**: пустой / длиннее 250 символов → `400`; спецсимволы не ломают `tsquery`.

## Вне текущего scope (заглушки)

- **Семантический поиск / Qdrant**: `message_index.NullIndexer`, `semantic_search`,
  `embeddings` — заглушки, вектор отключён.
- **Alembic-миграции** — каркас без ревизий.


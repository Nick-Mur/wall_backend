# Проектная работа 

## Этап 1: Проектирование доменной области

# Цель:
Основная задача системы - безопасная публикация контента с автоматической модерацией, поддержкой анонимности и масштабируемым поиском.

#  Бизнес-контекст:
Микросервисная платформа “The Wall” - сервис публикации пользовательских сообщений с поиском, модерацией и управлением жизненным циклом записей.

#  Основные сценарии:
1. Публикация записи
   - Пользователь отправляет текст
   - Система проверяет его мягкой (предупреждение) и жесткой (блокировка неприемлемого контента) модерацией
   - При успехе запись сохраняется и становится видимой на основной странице
2. Поиск записей
  - Подстроковый поиск (ILIKE)
  - Подстрочный поиск (PostgreSQL)
3. Управление видимостью записи (заготовка под будущее)
  - Скрыть запись (hide)
  - Убрать авторство (detach)
  - Стереть (hide + detach)
4. Модерация
  - Soft pipeline (предупреждение, без блокировки)
  - Hard pipeline (блокировка при использовании неприемлемого контента)
  - Проверка дублей по хешу текста

#  Сущности:
- Message(id, text, author_id, hidden, created_at)
- MessageRef(id, reference(id сообщения на которое ссылаемся))
- User(author_id) (заготовка на будущее для авторизации)

#  Связь между сущностями:
- Message → references → Message
- Message → author_id → User (Заготовка на будущее)

#  Ограничения:
1. text:
   - Текст не пустой
   - Максимум n символов
2. references[]:
   - Максимум N ссылок
   - Каждый элемент - UUID существующей записи (36 символов)
   - Дубликаты удаляются автоматически
3. Visibility constraint:
   - работаем только с видимыми записями (hidden = True записи не участвуют в поиске и считаются мягко уудаленными)

#  Бизнес-правила:
- Soft pipeline(не блокирует публикацию, все шаги выполняются всегда)
- Hard pipeline(Блокирует публикацию при первом срабатывании (fail-fast))
- Duplicate detection(повторная публикация блокируется)
- Спрятанные публикации не участвуют в поиске

# UML-диаграмма:
[Здесь UML-диаграмма](проект.png)

## Этап 2: Проектирование API и контрактов

# Разделение системы на сервисы:

#### Сервис message (:8002)
Отвечает за:
- публикацию
- модерацию
- duplicate detection
- управление сообщениями (hide / detach / erase)

#### Сервис search (:8004)
Отвечает за:
- substring search
- substring search
- получение записи по UUID

# API:

#### MESSAGE SERVICE (:8002)
1. POST /messages(создать новое сообщение)
Вход:
- text (текст записи)
- references[] (на что ссылается сообщение)
Выход:
- Успех(status, id, warnings (мягкие предупреждения))
- Ошибка(status, reason (жеская модерация))

2. PATCH /messages/{id}/hide(скрыть сообщение) (Заготовка на будущее)
Вход:
- author_id
Выход:
- status (успешность операции)

3. PATCH /messages/{id}/detach(Отвязать автора) (Заготовка на будущее)
Вход:
- author_id
Выход:
- status

hide + detach - жесткое удаление

#### SEARCH SERVICE (:8004)

1. GET /search/messages/substring
Query:
- q (запрос)
Выход:
- массив id сообщений подходящих под поиск

2. GET /search/messages/{id}
Выход:
- status

# Контракты:

1.  MessageRequest (POST /messages)

```
{
  "text": "string",
  "references": ["uuid"]
}
```

2.  MessageResponse

```
{
  "id": "uuid",
  "text": "string",
  "author_id": "uuid | null",
  "created_at": "ISO 8601"
}
```

3. MessageResult (search service)
```
{
  "id": "uuid",
  "text": "string",
  "author_id": "uuid | null",
  "created_at": "ISO 8601"
}
```

4. POST /messages SUCCESS RESPONSE
```
{
  "status": "published",
  "message_id": "uuid",
  "warnings": []
}
```

5. POST /messages ERROR RESPONSE
```
{
  "verdict": "rejected",
  "reason": "string"
}
```

### Обработка ошибок:

# Message Service

| Код | Значение |
|-----|----------|
| 201 | created / published |
| 400 | invalid input |
| 401 | no token (если нужен) |
| 403 | не автор сообщения |
| 409 | duplicate message |
| 422 | hard moderation reject |

---
# Search Service

| Код | Значение |
|-----|----------|
| 200 | success |
| 400 | invalid q |
| 404 | message not found |



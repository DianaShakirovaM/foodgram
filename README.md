# Foodgram

Foodgram — это онлайн-платформа для публикации кулинарных рецептов. Пользователи могут создавать свои рецепты, подписываться на других авторов, добавлять рецепты в избранное и формировать список покупок для выбранных блюд.

## Основные возможности
- Публикация рецептов с фото, описанием и списком ингредиентов
- Добавление в избранное для быстрого доступа
- Список покупок с возможностью скачивания
- Подписки на авторов и лента их рецептов
- Поиск по тегам (завтрак, обед, ужин)
---
## Автор
**Диана Шакирова**  
[![GitHub](https://img.shields.io/badge/GitHub-DianaShakirovaM-black)](https://github.com/DianaShakirovaM)  

## Установка

### Технологии
- Backend: Django 3.2 + Django REST Framework
- База данных: PostgreSQL
- Аутентификация: Djoser

### Требования
- Python 3.9+
- PostgreSQL
- Docker

### Локальный запуск
1. Клонируйте репозиторий:
```bash
   git clone https://github.com/DianaShakirovaM/foodgram.git
   cd foodgram
```
2. Установите зависимости:
```bash
  python -m venv venv
  source venv/bin/activate
  cd backend
  pip install -r requirements.txt
```
3. Импортируйте фикстуры и примените миграции:
```bash
  python manage.py migrate
  python manage.py import_ingredients_json
  python manage.py import_tags_json
```
4. Запустите сервер:
```bash
  python manage.py runserver
```
---
## Доступы
 - [Foodgram](https://myyafoodgram.zapto.org/)
 - [Админ-панель](https://myyafoodgram.zapto.org/admin/)
 - [API](https://myyafoodgram.zapto.org/api/)
 - [API документация](https://myyafoodgram.zapto.org/api/docs/)
 ---
## Примеры запросов
- Получить все рецепты
```http
GET /api/recipes/
```
### Пример ответа
```json
{
  "count": 123,
  "next": "http://myyafoodgram.zapto.org/api/recipes/?page=4",
  "previous": "http://myyafoodgram.zapto.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Иванов",
        "is_subscribed": false,
        "avatar": "http://myyafoodgram.zapto.org/media/users/image.png"
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://myyafoodgram.zapto.org/media/recipes/images/image.png",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```
- Создать новый рецепт (требуется аутентификация):
```http
POST /api/recipes/
Content-Type: application/json
Authorization: Token ваш_токен

{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
### Пример ответа
```json
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://myyafoodgram.zapto.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://myyafoodgram.zapro.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```
- Удалить рецепт из списка покупок (требуется аутентификация):
```bash
DELETE api/recipes/{id}/shopping_cart/
```
- Посмотреть все мои подписки
```bash
GET /api/users/subscriptions/
```
### Пример ответа
```json
{
  "count": 123,
  "next": "http://myyafoodgram.zapto.org/api/users/subscriptions/?page=4",
  "previous": "http://myyafoodgram.zapto.org/api/users/subscriptions/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Иванов",
      "is_subscribed": true,
      "recipes": [
        {
          "id": 0,
          "name": "string",
          "image": "http://myyafoodgram.zapto.org/media/recipes/images/image.png",
          "cooking_time": 1
        }
      ],
      "recipes_count": 0,
      "avatar": "http://myyafoodgram.zapto.org/media/users/image.png"
    }
  ]
}
```


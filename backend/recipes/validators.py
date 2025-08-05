from django.contrib.auth.validators import UnicodeUsernameValidator


class FoodgramUsernameValidator(UnicodeUsernameValidator):
    """Кастомный валидатор имени пользователя."""

    regex = r'^[\w.@+-]+\Z'
    message = (
        'Введите правильное имя пользователя.'
        'Оно может содержать только буквы, '
        'цифры и знаки @.+-_'
    )

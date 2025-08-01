from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGTH, FIRST_NAME_LENGTH, LAST_NAME_LENGTH


class FoodgramUser(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField('Почта', unique=True, max_length=EMAIL_LENGTH)
    avatar = models.ImageField(
        'Аватар', upload_to='users', default=None, null=True
    )
    first_name = models.CharField('Имя', max_length=FIRST_NAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_LENGTH)
    is_subscribed = models.BooleanField('Подписка', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username

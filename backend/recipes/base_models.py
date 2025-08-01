from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseRecipeModel(models.Model):
    """Базовая модель для создания рецепта."""

    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        abstract = True


class BaseUserRecipeModel(models.Model):
    """Абстрактная базовая модель для связей пользователь-рецепт."""

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('owner', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.owner} - {self.recipe}'

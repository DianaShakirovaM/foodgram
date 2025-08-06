from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from .constants import (
    EMAIL_LENGTH,
    FIRST_NAME_LENGTH,
    LAST_NAME_LENGTH,
    MIN_AMOUNT,
    MIN_COOKING_TIME
)


class FoodgramUser(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=(
                    'Имя пользователя содержит недопустимые символы.'
                    'Используйте только буквы, цифры и знаки @.+-_'
                )
            )
        ],
    )
    email = models.EmailField('Почта', unique=True, max_length=EMAIL_LENGTH)
    avatar = models.ImageField(
        'Аватар', upload_to='users', default=None, null=True
    )
    first_name = models.CharField('Имя', max_length=FIRST_NAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=LAST_NAME_LENGTH)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self) -> str:
        return self.username


class BaseUserRecipeModel(models.Model):
    """Абстрактная базовая модель для связей пользователь-рецепт."""

    owner = models.ForeignKey(
        FoodgramUser,
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


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=128, unique=True)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_with_unit'
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега для рецепта."""

    name = models.CharField('Название', max_length=32, unique=True)
    slug = models.SlugField('Слаг', unique=True, max_length=32)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    author = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, null=True,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Фото', upload_to='recipes/images')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время (мин)',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связанная модель рецепта и продукта."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', default=1,
        validators=[MinValueValidator(MIN_AMOUNT)]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукт в рецепте'

    def __str__(self) -> str:
        return f'{self.recipe.name} - {self.ingredient.name}'


class ShoppingCart(BaseUserRecipeModel):
    """Модель списка покупок пользователя."""

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'


class Favorite(BaseUserRecipeModel):
    """Модель избранных рецептов пользователя."""

    class Meta(BaseUserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )

    following = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_following'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='prevent_self_follow'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.following.username}'

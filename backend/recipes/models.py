from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from api.fields import generate_short_link
from .base_models import BaseRecipeModel, BaseUserRecipeModel

MAX_LENGTH_SHORT_LINK = 10

User = get_user_model()


class Ingredient(BaseRecipeModel):
    """Модель ингредиента."""

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=10,
        default='g'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(BaseRecipeModel):
    """Модель тега для рецепта."""

    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""

    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Теги'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,
        related_name='recipes', verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name='recipes', through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    is_favorited = models.BooleanField('В избранном', default=False)
    is_in_shopping_cart = models.BooleanField(
        'В списке покупок', default=False
    )
    name = models.CharField('Название', max_length=255)
    image = models.ImageField('Фото', upload_to='recipes/images')
    text = models.TextField('Описание')
    cooking_time = models.FloatField(
        'Время приготовления', validators=[MinValueValidator(1)]
    )
    short_link = models.CharField(
        'Короткая ссылка',
        default=generate_short_link,
        max_length=MAX_LENGTH_SHORT_LINK,
        unique=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Связанная модель рецепта и тега."""

    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Тег'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self) -> str:
        return f'{self.recipe.name} - {self.tag.slug}'


class RecipeIngredient(models.Model):
    """Связанная модель рецепта и ингредиента."""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиент в рецепте'

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
        User,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Подписчик'
    )

    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
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

from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    FoodgramUser,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Favorite,
)


def count_method(field_name, description):
    """Создаёт метод для отображения количества связанных объектов."""
    @admin.display(description=description)
    def method(obj):
        return getattr(obj, field_name).count()
    return method


@admin.register(ShoppingCart, Favorite)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    """Базовый класс для моделей связи пользователь-рецепт."""

    list_display = ('id', 'owner', 'recipe')
    list_filter = ('owner', 'recipe__tags')
    search_fields = ('recipe__name', 'owner__email')


@admin.register(FoodgramUser)
class FoodgramUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name',
        'is_staff', 'recipe_count', 'follower_count', 'following_count'
    )
    list_display_links = ('id', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    readonly_fields = ('recipe_count', 'follower_count', 'following_count')
    recipe_count = count_method('recipes', 'Рецептов')
    follower_count = count_method('followers', 'Подписчиков')
    following_count = count_method('following', 'Подписок')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorites_count', 'ingredients_list',
        'tags_list', 'image_preview'
    )
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author')
    readonly_fields = ('favorites_count',)
    favorites_count = count_method('favorites', 'В избранном')

    @admin.display(description='Ингредиенты')
    @mark_safe
    def ingredients_list(self, recipe):
        return '<br>'.join(
            f'{ing.ingredient.name} - {ing.amount} '
            f'{ing.ingredient.measurement_unit}'
            for ing in recipe.recipe_ingredients.all()
        )

    @admin.display(description='Теги')
    @mark_safe
    def tags_list(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Превью')
    @mark_safe
    def image_preview(self, obj):
        if obj.image:
            return (
                f'<img src="{obj.image.url}" '
                'style="max-height: 100px; max-width: 100px;" />'
            )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = 50
    readonly_fields = ('recipe_count',)
    recipe_count = count_method(
        'recipe_ingredients', 'Используется в рецептах'
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('recipe_count',)
    list_per_page = 20
    recipe_count = count_method('recipes', 'Кол-во рецептов')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = (
        'following__username', 'user__username',
        'following__email', 'user__email'
    )
    list_filter = ('user', 'following')

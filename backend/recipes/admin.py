from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin

from .filters import CookingTimeFilter
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
    def method(self, obj):
        return getattr(obj, field_name).count()
    return method


def image_display(
        image_field='image', description='Превью',
        max_height=100, max_width=100
):
    """
    Создаёт метод для отображения превью изображения.
    """
    @admin.display(description=description)
    @mark_safe
    def method(self, obj):
        image = getattr(obj, image_field, None)
        if image and hasattr(image, 'url'):
            return (
                f'<img src="{image.url}" '
                f'style="max-height: {max_height}px; '
                f'max-width: {max_width}px;" />'
            )
        return ''
    return method


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'id', 'email', 'full_name', 'username', 'avatar_display',
        'recipe_count', 'follower_count', 'following_count'
    )
    list_display_links = ('id', 'email')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_active')
    readonly_fields = (
        'recipe_count', 'follower_count', 'following_count', 'avatar_display'
    )
    recipe_count = count_method('recipes', 'Рецептов')
    follower_count = count_method('followers', 'Подписчиков')
    following_count = count_method('authors', 'Подписок')
    avatar_display = image_display('avatar', 'Аватар')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': (
            'first_name', 'last_name', 'email', 'avatar')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    @admin.display(description='ФИО')
    def full_name(self, obj):
        return f'{obj.last_name} {obj.first_name}'


@admin.register(ShoppingCart, Favorite)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    """Базовый класс для моделей связи пользователь-рецепт."""

    list_display = ('id', 'owner', 'recipe')
    list_filter = ('owner', 'recipe__tags')
    search_fields = ('recipe__name', 'owner__email')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cooking_time', 'author',
        'favorites_count', 'ingredients_list',
        'tags_list', 'image_preview'
    )
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username')
    list_filter = ('tags', 'author', CookingTimeFilter)
    readonly_fields = ('favorites_count', 'image_preview')
    favorites_count = count_method('favorites', 'В избранном')
    image_preview = image_display('image')
    inlines = (RecipeIngredientInline,)

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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = 50
    readonly_fields = ('recipe_count',)
    recipe_count = count_method(
        'recipe_ingredients', 'В рецептах'
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('recipe_count',)
    list_per_page = 20
    recipe_count = count_method('recipes', 'Рецептов')


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


admin.site.unregister(Group)

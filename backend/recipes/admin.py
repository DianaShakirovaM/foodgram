from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (
    FoodgramUser, Follow, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag, Favorite
)


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

    def recipe_count(self, user):
        return user.recipes.count()
    recipe_count.short_description = 'Рецептов'

    def follower_count(self, user):
        return user.followers.count()
    follower_count.short_description = 'Подписчиков'

    def following_count(self, user):
        return user.following.count()
    following_count.short_description = 'Подписок'


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

    def favorites_count(self, recipe):
        return recipe.favorites.count()
    favorites_count.short_description = 'В избранном'

    def ingredients_list(self, recipe):
        ingredients = recipe.recipe_ingredients.all()
        items = [
            f'<li>{ing.ingredient.name} - {ing.amount} '
            f'{ing.ingredient.measurement_unit}</li>'
            for ing in ingredients
        ]
        return mark_safe(f'<ul>{"".join(items)}</ul>')
    ingredients_list.short_description = 'Ингредиенты'

    def tags_list(self, recipe):
        tags = recipe.tags.all()
        items = [f'<li>{tag.name}</li>' for tag in tags]
        return mark_safe(f'<ul>{"".join(items)}</ul>')
    tags_list.short_description = 'Теги'

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" '
                'style="max-height: 100px; max-width: 100px;" />'
            )
        return 'Нет изображения'
    image_preview.short_description = 'Превью'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipe_count')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    list_per_page = 50
    readonly_fields = ('recipe_count',)

    def recipe_count(self, ingredient):
        return ingredient.recipe_ingredients.count()
    recipe_count.short_description = 'Используется в рецептах'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipe_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('recipe_count',)
    list_per_page = 20

    def recipe_count(self, tag):
        return tag.recipes.count()
    recipe_count.short_description = 'Кол-во рецептов'


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


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'recipe')
    list_filter = ('owner', 'recipe__tags')
    search_fields = ('recipe__name', 'owner__email')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'recipe')
    list_filter = ('owner', 'recipe__tags')
    search_fields = ('recipe__name', 'owner__email')

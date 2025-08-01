from django.contrib import admin

from .models import Follow, Ingredient, Recipe, ShoppingCart, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('author', 'name')
    list_filter = ('tags', 'author')
    list_per_page = 25


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = 50


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    search_fields = ('following__username', 'user__username')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('owner', 'recipe')
    list_filter = ('owner', 'recipe__tags')
    search_fields = ('recipe__name', 'owner__email')

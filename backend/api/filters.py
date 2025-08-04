from django_filters import FilterSet, ModelMultipleChoiceFilter, NumberFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для рецептов по автору, тегам, наличию в корзине и избранному."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = NumberFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_is_in_shopping_cart(self, recipe, name, value):
        if self.request.user.is_anonymous:
            return recipe.none()
        if value:
            return recipe.filter(
                shopping_carts__owner=self.request.user
            )
        return recipe

    def filter_is_favorited(self, recipe, name, value):
        if self.request.user.is_anonymous:
            return recipe.none()
        if value:
            return recipe.filter(
                favorites__owner=self.request.user
            )
        return recipe

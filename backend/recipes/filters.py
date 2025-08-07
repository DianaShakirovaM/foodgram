from django.contrib import admin


class CookingTimeFilter(admin.SimpleListFilter):
    """Фильтр по времени приготовления."""

    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return (
            ('fast', 'Быстрые'),
            ('medium', 'Средние'),
            ('long', 'Долгие'),
        )

    def queryset(self, request, recipe):
        if self.value() == 'fast':
            return recipe.filter(cooking_time__lt=30)
        if self.value() == 'medium':
            return recipe.filter(cooking_time__gte=30, cooking_time__lte=60)
        if self.value() == 'long':
            return recipe.filter(cooking_time__gt=60)
        return recipe

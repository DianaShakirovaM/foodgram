from django.shortcuts import redirect
from rest_framework.exceptions import NotFound


def short_redirect(self, request, recipe_id=None):
    """
    Обработчик коротких ссылок на рецепты.
    """
    if not self.get_queryset().filter(pk=recipe_id).exists():
        raise NotFound(
            detail={'error': f'Рецепт с ID={recipe_id} не найден.'}
        )
    return redirect(f'/recipes/{recipe_id}')

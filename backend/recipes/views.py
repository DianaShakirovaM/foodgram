from django.shortcuts import redirect
from django.http import Http404

from .models import Recipe


def short_redirect(request, recipe_id):
    """
    Обработчик коротких ссылок на рецепты.
    """
    if not Recipe.objects.filter(pk=recipe_id).exists():
        raise Http404(f'Рецепт с id={recipe_id} не найден.')
    return redirect('http://localhost/recipes/3')

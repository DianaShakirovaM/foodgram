from collections import defaultdict

from django.db.models import F
from django.template.loader import render_to_string
from django.utils import timezone


def generate_shopping_list(user):
    shopping_cart = user.shopping_carts.select_related(
        'recipe').prefetch_related('recipe__ingredients').all()
    recipes = [item.recipe for item in shopping_cart]
    recipe_ingredients = defaultdict(list)

    for item in shopping_cart:
        ingredients = item.recipe.ingredients.all().values(
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )
        recipe_ingredients[item.recipe].extend(ingredients)
    recipe_ingredients = dict(recipe_ingredients)
    context = {
        'date': timezone.now().strftime('%d.%m.%Y'),
        'recipes': [
            {
                'recipe': recipe,
                'ingredients': recipe_ingredients[recipe]
            }
            for recipe in recipes
        ]
    }
    return render_to_string('shopping_list.txt', context)

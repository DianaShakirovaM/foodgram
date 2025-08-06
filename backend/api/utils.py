from collections import defaultdict
from django.template.loader import render_to_string
from django.utils import timezone


def generate_shopping_list(user):
    MONTH_NAMES = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    now = timezone.now()
    day = now.day
    month = MONTH_NAMES[now.month]
    year = now.year
    formatted_date = f'{day} {month} {year}'

    recipes = [
        item.recipe for item in user.shopping_carts.select_related('recipe')
    ]
    ingredients = defaultdict(lambda: {'amount': 0, 'unit': ''})
    for cart_item in user.shopping_carts.all():
        for ingredient in cart_item.recipe.ingredients.all():
            amount = ingredient.recipe_ingredients.get(
                recipe=cart_item.recipe).amount
            ingredients[ingredient.name]['amount'] += amount
            ingredients[ingredient.name]['unit'] = ingredient.measurement_unit

    context = {
        'date': formatted_date,
        'recipes': recipes,
        'total_ingredients': sorted(ingredients.items())
    }
    return render_to_string('shopping_list.txt', context)

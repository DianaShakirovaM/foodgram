from recipes.models import Ingredient
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт ингредиентов из JSON."""

    filename = 'ingredients.json'
    model = Ingredient

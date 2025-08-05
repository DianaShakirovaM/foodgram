import csv

from recipes.models import Ingredient
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт ингредиентов из CSV."""

    filename = 'ingredients.csv'
    model = Ingredient

    def load_file(self, file):
        return list(csv.reader(file))

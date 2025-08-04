import csv

from recipes.models import Ingredient
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт ингредиентов из CSV."""

    filename = 'ingredients.csv'
    model = Ingredient

    def load_file(self, file):
        return list(csv.reader(file))

    def process_data(self, data):
        ingredients = []
        for row in data:
            ingredients.append(Ingredient(
                name=row[0].strip(),
                measurement_unit=row[1].strip()
            ))

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Добавлено {len(ingredients)} ингредиентов из CSV'
            )
        )

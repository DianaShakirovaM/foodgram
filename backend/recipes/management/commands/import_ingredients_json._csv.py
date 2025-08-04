import json

from recipes.models import Ingredient
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт ингредиентов из JSON."""

    filename = 'ingredients.json'
    model = Ingredient

    def load_file(self, file):
        return json.load(file)

    def process_data(self, data):
        ingredients = []
        for item in data:
            ingredients.append(Ingredient(
                name=item['name'].strip(),
                measurement_unit=item['measurement_unit'].strip()
            ))

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Добавлено {len(ingredients)} ингредиентов из JSON'
            )
        )

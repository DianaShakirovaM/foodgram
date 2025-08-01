import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_DIR = os.path.join(settings.BASE_DIR, '', 'data')


class Command(BaseCommand):
    help = 'Загружает данные из CSV'

    def handle(self, *args, **options):
        self.load_ingredients()

    def load_csv(self, filename):
        with open(
            os.path.join(DATA_DIR, filename), encoding='utf-8'
        ) as csvfile:
            return list(csv.reader(csvfile))

    def load_ingredients(self):
        ingredients = self.load_csv('ingredients.csv')
        for row in ingredients:
            try:
                if len(row) < 2:
                    raise ValueError(f"Недостаточно данных в строке: {row}")

                ingredient_name = row[0].strip()
                measurement_unit = row[1].strip()

                Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                )
                self.stdout.write(self.style.SUCCESS(
                    'Успешно добавлен ингредиент: '
                    f'{ingredient_name} ({measurement_unit})'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Ошибка при добавлении ингредиента {row}: {str(e)}'
                ))

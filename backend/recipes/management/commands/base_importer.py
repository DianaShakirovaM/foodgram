import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')


class BaseImportCommand(BaseCommand):
    """Базовый класс для импорта данных."""

    filename = None
    model = None
    help = 'Загружает данные из файла'

    def handle(self, *args, **options):
        try:
            filepath = os.path.join(DATA_DIR, self.filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                items = [self.model(**item) for item in self.load_data(file)]
                count = len(
                    self.model.objects.bulk_create(
                        items, ignore_conflicts=True
                    )
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Добавлено {count} записей из {self.filename}'
                ))
        except Exception:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при загрузке данных в файле {self.filename}'
                )
            )

    def load_data(self, file):
        return json.load(file)

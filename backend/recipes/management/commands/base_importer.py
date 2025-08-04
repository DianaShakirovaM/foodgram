import os

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
                data = self.load_file(file)
                self.process_data(data)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные из {self.filename} успешно загружены'
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'Файл {self.filename} не найден в папке data'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при загрузке данных: {str(e)}')
            )

    def load_file(self, file):
        raise NotImplementedError

    def process_data(self, data):
        raise NotImplementedError

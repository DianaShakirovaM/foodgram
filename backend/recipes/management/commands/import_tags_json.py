import json

from recipes.models import Tag
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт тегов из JSON."""

    filename = 'tags.json'
    model = Tag

    def load_file(self, file):
        return json.load(file)

    def process_data(self, data):
        tags = []
        for item in data:
            tags.append(Tag(
                name=item['name'].strip(),
                slug=item['slug'].strip(),
            ))

        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {len(tags)} тегов')
        )

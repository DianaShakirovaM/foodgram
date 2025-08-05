from recipes.models import Tag
from .base_importer import BaseImportCommand


class Command(BaseImportCommand):
    """Импорт тегов из JSON."""

    filename = 'tags.json'
    model = Tag

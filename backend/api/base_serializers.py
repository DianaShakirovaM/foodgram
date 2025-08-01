from rest_framework import serializers


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для действий с рецептами (корзина/избранное)."""

    class Meta:
        abstract = True
        fields = '__all__'

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': instance.recipe.image.url
            if instance.recipe.image else None,
            'cooking_time': instance.recipe.cooking_time
        }

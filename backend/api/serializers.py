from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.constants import COOKING_TIME_MIN_VALUE
from recipes.models import (
    Follow,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .fields import Base64Field

RECIPE_MIN_VALUE_AMOUNT = 1


User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'is_subscribed', 'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and Follow.objects.filter(
                user=request.user, following=user
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с аватаром."""

    avatar = Base64Field()

    class Meta:
        model = User
        fields = ('avatar', )


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для краткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class SubscriptionSerializer(FoodgramUserSerializer):
    """Сериализатор подписок с информацией о пользователе и его рецептах."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes_count', 'avatar', 'recipes'
        )

    def get_recipes(self, user):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = (
            user.recipes.all()[:int(recipes_limit)] if recipes_limit
            else user.recipes.all()
        )
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепта и ингредиента с доп. полями."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(min_value=RECIPE_MIN_VALUE_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseRecipeEditCreateSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для изменения/создания рецептов."""

    author = FoodgramUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64Field(required=False)
    cooking_time = serializers.IntegerField(min_value=COOKING_TIME_MIN_VALUE)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    def _find_duplicates(self, items_id):
        seen = set()
        duplicates = set()
        for item_id in items_id:
            if item_id in seen:
                duplicates.add(item_id)
            else:
                seen.add(item_id)
        return duplicates

    def validate_recipe_data(self, tags, ingredients):
        """Общая валидация тегов и ингредиентов."""
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients':
                    'Рецепт должен содержать хотя бы один ингредиент.'
                }
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Рецепт должен содержать хотя бы один тег'}
            )

        tags_id = [tag.id for tag in tags]
        ingredients_id = [item['ingredient'].id for item in ingredients]
        tags_duplicates = self._find_duplicates(tags_id)
        ingredients_duplicates = self._find_duplicates(ingredients_id)

        if tags_duplicates:
            raise serializers.ValidationError(
                {
                    'tags': 'Обнаружены повторяющиеся теги: '
                    f'{", ".join(map(str, tags_duplicates))}'
                }
            )

        if ingredients_duplicates:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Обнаружены повторяющиеся ингредиенты: '
                    f'{", ".join(map(str, ingredients_duplicates))}'
                }
            )

        return {'tags': tags, 'ingredients': ingredients}

    def create_recipe_relations(self, recipe, tags, ingredients):
        """Создание связей рецепта с тегами и ингредиентами."""

        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = FoodgramUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and Favorite.objects.filter(
                owner=request.user, recipe=recipe
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and ShoppingCart.objects.filter(
                owner=request.user, recipe=obj
            ).exists()
        )


class RecipeCreateSerializer(BaseRecipeEditCreateSerializer):
    """Сериализатор для создания рецепта."""

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')

        self.validate_recipe_data(tags, ingredients)
        recipe = super().create(validated_data)
        self.create_recipe_relations(recipe, tags, ingredients)

        return recipe

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe, context=self.context).data


class RecipeEditSerializer(BaseRecipeEditCreateSerializer):
    """Сериализатор для редактирования рецепта."""

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('recipe_ingredients', None)
        self.validate_recipe_data(tags, ingredients)
        # Удаляем старые связи перед обновлением
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe = super().update(recipe, validated_data)
        self.create_recipe_relations(recipe, tags, ingredients)
        return recipe

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe, context=self.context).data

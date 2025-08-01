from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Follow, Favorite, Ingredient, Recipe,
    RecipeIngredient, RecipeTag, ShoppingCart, Tag
)
from .base_serializers import BaseRecipeActionSerializer
from .fields import Base64Field

User = get_user_model()


class RegistrationSerializer(UserCreateSerializer):
    """Сериализатор для регистрации."""

    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )


class FoodgramUserSerializer(serializers.ModelSerializer):
    """Сериализатор для автора рецепта."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=user).exists()


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


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписок с информацией о пользователе и его рецептах."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=user).exists()

    def get_recipes(self, user):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = (
            user.recipes.all()[:int(recipes_limit)] if recipes_limit
            else user.recipes.all()
        )
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и валидации подписок."""

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate_following(self, user):
        if self.context['request'].user == user:
            raise serializers.ValidationError(
                'Нельзя подписываться на себя!',
                code='invalid_subscription'
            )
        return user

    def to_representation(self, user):
        return SubscriptionSerializer(
            user.following, context=self.context).data


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
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для рецептов."""

    author = FoodgramUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    image = Base64Field(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

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

        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться.'}
            )

        if len(tags_id) != len(set(tags_id)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'}
            )

        return tags, ingredients

    def create_recipe_relations(self, recipe, tags, ingredients):
        """Создание связей рецепта с тегами и ингредиентами."""
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(owner=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            owner=request.user, recipe=obj).exists()


class RecipeCreateSerializer(BaseRecipeSerializer):
    """Сериализатор для создания рецепта."""

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')

        self.validate_recipe_data(tags, ingredients)

        recipe = Recipe.objects.create(**validated_data)
        self.create_recipe_relations(recipe, tags, ingredients)

        return recipe

    def to_representation(self, recipe):
        return RecipeSerializer(recipe, context=self.context).data


class RecipeEditSerializer(BaseRecipeSerializer):
    """Сериализатор для редактирования рецепта."""

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('recipe_ingredients', None)

        self.validate_recipe_data(tags, ingredients)

        # Удаляем старые связи перед обновлением
        RecipeTag.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.filter(recipe=recipe).delete()

        recipe = super().update(recipe, validated_data)
        self.create_recipe_relations(recipe, tags, ingredients)

        return recipe

    def to_representation(self, recipe):
        representation = super().to_representation(recipe)
        representation['tags'] = TagSerializer(
            recipe.tags.all(),
            many=True
        ).data
        return representation


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    """Сериализатор списка покупок."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = ShoppingCart
        fields = ('owner', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('recipe', 'owner')
            )
        ]


class FavoriteSerializer(BaseRecipeActionSerializer):
    """Сериализатор для отображения избранного."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = Favorite
        fields = ('owner', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('recipe', 'owner')
            )
        ]

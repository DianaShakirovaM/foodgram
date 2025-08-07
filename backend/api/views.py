from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from .filters import RecipeFilter, IngredientFilter
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer,
    IngredientSerializer,
    RecipeEditCreateSerializer,
    RecipeReadSerializer,
    ShortRecipeSerializer,
    SubscribedUserSerializer,
    TagSerializer,
)
from .utils import generate_shopping_list

User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    pagination_class = Pagination

    @action(
        detail=False,
        methods=('get',),
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        methods=('put', 'delete'),
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
        url_name='me-avatar'
    )
    def me_avatar(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'DELETE':
            user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = AvatarSerializer(
            instance=user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=('get',),
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,),
        pagination_class=Pagination
    )
    def subscriptions(self, request):
        serializer = SubscribedUserSerializer(
            self.paginate_queryset(
                User.objects.filter(authors__user=request.user)
                .prefetch_related('recipes')
            ),
            many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=request.user, following_id=id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        following = get_object_or_404(User, pk=id)
        if request.user == following:
            raise serializers.ValidationError(
                {'error': 'Нельзя подписываться на себя!'}
            )
        _, created = Follow.objects.get_or_create(
            user=request.user, following=following
        )
        if not created:
            raise serializers.ValidationError(
                {'error': f'Вы уже подписаны на {following.username}'}
            )

        serializer = SubscribedUserSerializer(
            following,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    pagination_class = Pagination
    queryset = Recipe.objects.all().order_by('-pub_date')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['partial_update', 'create']:
            return RecipeEditCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe_exists = self.get_queryset().filter(pk=pk).exists()
        if not recipe_exists:
            raise NotFound(
                detail={'error': f'Рецепт с id={pk} не найден.'}
            )
        return Response(
            {
                'short-link':
                request.build_absolute_uri(
                    reverse('recipes:short-link', kwargs={'recipe_id': pk})
                )
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._handle_favorite_or_cart(request, pk, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self._handle_favorite_or_cart(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            generate_shopping_list(request.user),
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )

    def _handle_favorite_or_cart(self, request, pk, model):
        user = request.user
        if request.method == 'DELETE':
            get_object_or_404(model, owner=request.user, recipe_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        recipe = get_object_or_404(Recipe, pk=pk)
        _, created = model.objects.get_or_create(
            owner=user,
            recipe=recipe,
        )
        if not created:
            raise serializers.ValidationError(
                {'error': f'Рецепт {recipe.name} уже добавлен в '
                          f'{self._get_model_name(model)}'}
            )

        return Response(
            ShortRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

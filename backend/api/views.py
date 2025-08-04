from io import BytesIO

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    RecipeCreateSerializer,
    RecipeEditSerializer,
    RecipeReadSerializer,
    ShortRecipeSerializer,
    SubscriptionSerializer,
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
        serializer = SubscriptionSerializer(
            self.paginate_queryset(
                User.objects.filter(following__user=request.user)
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
        following = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            if request.user == following:
                return Response(
                    {'error': 'Нельзя подписываться на себя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Follow.objects.filter(
                user=request.user, following=following
            ).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Follow.objects.create(user=request.user, following=following)
            serializer = SubscriptionSerializer(following)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Follow,
            following=following,
            user=request.user
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    pagination_class = Pagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['partial_update']:
            return RecipeEditSerializer
        elif self.action in ['create']:
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        url_path='s/<int:recipe_id>/',
        url_name='short-link'
    )
    def short_redirect(self, request, recipe_id=None):
        """
        Обработчик коротких ссылок на рецепты.
        """
        if not self.get_queryset().filter(pk=recipe_id).exists():
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        return redirect(f'/recipes/{recipe_id}')

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe_exists = self.get_queryset().filter(pk=pk).exists()
        if not recipe_exists:
            return Response(
                {'recipe': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        short_url = request.build_absolute_uri(
            reverse('api:short-link', kwargs={'recipe_id': pk})
        )
        return Response(
            {'short-link': short_url},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._handle_favorite_or_cart(request, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self._handle_favorite_or_cart(request, pk, 'shopping_cart')

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_list = generate_shopping_list(request.user)
        file = BytesIO(shopping_list.encode('utf-8'))
        return FileResponse(
            file,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )

    def _handle_favorite_or_cart(self, request, pk, action_type='favorite'):
        user = request.user
        model = ShoppingCart if action_type == 'shopping_cart' else Favorite
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'DELETE':
            deleted_count, _ = model.objects.filter(
                owner=user, recipe=recipe).delete()

            if not deleted_count:
                return Response(
                    {'error': f'Рецепт не был добавлен ранее в {action_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(status=status.HTTP_204_NO_CONTENT)

        _, created = model.objects.get_or_create(
            owner=user,
            recipe=recipe,
        )

        if not created:
            return Response(
                {'error': f'Рецепт уже добавлен в {action_type}'},
                status=status.HTTP_400_BAD_REQUEST
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


class RecipeRedirectView(APIView):
    """Обрабатывает переходы по коротким ссылкам."""

    def get(self, request, recipe_id):
        recipe_exists = Recipe.objects.filter(pk=recipe_id).exists()
        if not recipe_exists:
            return Response(
                {'error': 'Рецепт не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        return redirect(f'/recipes/{recipe_id}')

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenCreateView, TokenDestroyView, UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite, Follow, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)
from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, FavoriteSerializer, FollowSerializer,
    IngredientSerializer, RecipeCreateSerializer, RecipeEditSerializer,
    RecipeSerializer, ShoppingCartSerializer, SubscriptionSerializer,
    TagSerializer
)

User = get_user_model()


class CustomTokenCreateView(TokenCreateView):
    """Вьюсет для создания токена."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return Response(
                {'auth_token': response.data['auth_token']},
                status=status.HTTP_200_OK
            )
        return response


class CustomTokenDestroyView(TokenDestroyView):
    """Вьюсет для удаления токена."""

    def post(self, request):
        super().post(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FoodgramUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    pagination_class = CustomPagination

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
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        serializer = SubscriptionSerializer(
            self.paginate_queryset(
                User.objects.filter(followers__user=request.user)
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
            serializer = FollowSerializer(
                data={'user': request.user.id, 'following': following.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Follow.objects.filter(
            following=following,
            user=request.user
        )

        if not subscription:
            return Response(
                {'error': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""

    pagination_class = CustomPagination
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['partial_update']:
            return RecipeEditSerializer
        elif self.action in ['create']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        if request.method.lower() == 'put':
            raise MethodNotAllowed(
                method='PUT',
                detail='Используйте PATCH для частичного '
                       'обновления вместо PUT.'
            )
        return super().update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=('get',),
        url_path='get-link'
    )
    def get_link(self, request, pk):
        recipe = self.get_object()
        return Response(
            {
                'short-link': f'{request.scheme}://'
                f'{request.get_host()}/s/{recipe.short_link}'
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._handle_favorite_or_cart(request, pk, 'favorite')

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
        user = request.user
        shopping_cart = user.shopping_carts.all()
        recipes = [item.recipe for item in shopping_cart]
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        shopping_list = 'Список покупок:\n\n'
        for item in ingredients:
            shopping_list += (
                f'{item["ingredient__name"]} - '
                f'{item["total_amount"]} '
                f'{item["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(shopping_list, content_type='text/plaint')
        response['Content-Disposition'] = ('attachment:'
                                           'filename="shopping_list.txt"')
        return response

    def _handle_favorite_or_cart(self, request, pk, action_type):
        recipe = self.get_object()
        user = request.user

        model, serializer_class = (
            (Favorite, FavoriteSerializer) if action_type == 'favorite'
            else (ShoppingCart, ShoppingCartSerializer)
        )

        if request.method == 'DELETE':
            recipe = model.objects.filter(owner=user, recipe=recipe)
            if not recipe:
                return Response(
                    {'error': 'Рецепт не был добавлен ранее'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = serializer_class(
            data={'owner': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('name')

        if search_query:
            queryset = queryset.filter(name__istartswith=search_query)
            if not queryset.exists():
                queryset = Ingredient.objects.filter(
                    name__icontains=search_query
                )

        return queryset


class RecipeRedirectView(APIView):
    """Вьюсет для перенаправления с короткой ссылки на рецепт. """

    def get(self, request, short_link):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return HttpResponseRedirect(
            f'/recipes/{recipe.id}/',
            status=302
        )

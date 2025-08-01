from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


v1_router = DefaultRouter()
v1_router.register('users', views.FoodgramUserViewSet)
v1_router.register('recipes', views.RecipeViewSet)
v1_router.register(
    'ingredients', views.IngredientViewSet, basename='ingredients'
)
v1_router.register('tags', views.TagViewSet)

auth_patterns = [
    path(
        'auth/token/login/', views.CustomTokenCreateView.as_view(),
        name='login'
    ),
    path(
        'auth/token/logout/', views.CustomTokenDestroyView.as_view(),
        name='logout'
    ),
]

urlpatterns = [
    path('', include(auth_patterns)),
    path('', include(v1_router.urls))
]

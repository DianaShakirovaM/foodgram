from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('users', views.FoodgramUserViewSet)
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register(
    'ingredients', views.IngredientViewSet, basename='ingredients'
)
router.register('tags', views.TagViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

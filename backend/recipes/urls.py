from django.urls import path

from .views import short_redirect

app_name = 'recipes'

urlpatterns = [
    path(
        's/<int:recipe_id>/', short_redirect,
        name='short-link'
    ),
]

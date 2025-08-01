from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Устанавливает права на измнение рецепта."""

    def has_object_permission(self, request, view, recipe):
        return (
            request.method in SAFE_METHODS or request.user == recipe.author
        )

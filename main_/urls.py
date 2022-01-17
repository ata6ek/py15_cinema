from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main_.views import PostViewSet, CategoryViewSet, FavoritesListView, LikesListView, ReviewViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('reviews', ReviewViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('favorites/', FavoritesListView.as_view()),
    path('likes/', LikesListView.as_view())
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main_.views import PostViewSet, ReviewViewSet, CategoryViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('reviews', ReviewViewSet)
router.register('categories', CategoryViewSet)

urlpatterns = [
    # path('categories/', CategoriesListView.as_view()),
    path('', include(router.urls))
]

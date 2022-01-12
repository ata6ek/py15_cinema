from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from main_.models import Category, Post, Review, Favorites
from main_.permissions import IsAuthor
from main_.serializers import CategorySerializer, PostSerializer, PostListSerializer, ReviewSerializer


# class CategoriesListView(ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthor]


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['title', 'text']
    filterset_fields = ['category']

    def get_serializer_class(self):
        serializer_class = super().get_serializer_class()
        if self.action == 'list':
            serializer_class = PostListSerializer
        return serializer_class

    def get_permissions(self):
        #создавать пост может залогиненный пользователь
        if self.action in ['create', 'add_to_favorites', 'remove_from_favorites']:
            return [IsAuthenticated()]
        # изменять и удалять только автор
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthor()]
        # просматривать могут все
        return []

    @action(['GET'], detail=True)
    def reviews(self, request, pk):
        post = self.get_object()
        reviews = post.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    #api/v1/posts/id/add_to_favorites/
    @action(['POST'], detail=True)
    def add_to_favorites(self, request, pk=None):
        post = self.get_object()
        if request.user.liked.filter(post=post).exists():
            return Response('Пост уже находится в избранных')
        Favorites.objects.create(post=post, user=request.user)
        return Response('Добавлено в избранное')

    @action(['POST'], detail=True)
    def remove_from_favorites(self, request, pk=None):
        post = self.get_object()
        if not request.user.liked.filter(post=post).exists():
            return Response('Пост не находится в списке избранных')
        request.user.liked.filter(post=post).delete()
        return Response('Пост удалён из избранных')


class ReviewViewSet(CreateModelMixin,
                     UpdateModelMixin,
                     DestroyModelMixin,
                     GenericViewSet):
        queryset = Review.objects.all()
        serializer_class = ReviewSerializer

        def get_permissions(self):
            # создавать пост может залогиненный пользователь
            if self.action == 'create':
                return [IsAuthenticated()]
            # изменять и удалять только автор
            elif self.action in ['update', 'partial_update', 'destroy']:
                return [IsAuthor()]
            # просматривать




# TODO: likes
# TODO: favorites
# TODO: pagination, filter
# TODO: rating
# TODO: swagger
# TODO: celery
# TODO: presentation
# TODO: video-youtube


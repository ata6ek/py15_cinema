from django.contrib.auth import get_user_model
from rest_framework import serializers

from main_.models import Category, Post, PostImage, PostVideo, Favorite, Review, Like
from main_.tasks import send_new_series

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostListSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user = serializers.CharField(source='user.name')

    class Meta:
        model = Post
        # exclude = ['user']
        fields = ['id', 'title', 'text', 'category', 'reviews', 'user', 'created_at', 'image', 'video']

    def get_image(self, post):
        first_image = post.pics.first()
        if first_image and first_image.image:
            return first_image.image.url
        return ''

    def get_video(self, post):
        first_video = post.trailer.first()
        if first_video and first_video.video:
            return first_video.video.url
        return ''

    def is_favorited(self, post):
        user = self.context.get('request').user
        return user.favorited.filter(post=post).exists()

    def is_liked(self, post):
        user = self.context.get('request').user
        return user.liked.filter(post=post).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user
        if user.is_authenticated:
            representation['is_favorited'] = self.is_favorited(instance)
            representation['is_liked'] = self.is_liked(instance)
        representation['likes_count'] = instance.likes.count()
        rating = ReviewSerializer(instance.reviews.all(), many=True).data
        try:
            fl = 0
            for ordered_dict in rating:
                fl += ordered_dict.get('rating')
            representation['rating_average'] = round(fl / instance.reviews.all().count(), 1)
            return representation
        except ZeroDivisionError:
            return representation


class ReviewSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(),
                                              write_only=True)

    class Meta:
        model = Review
        exclude = ['user']

    def validate(self, attrs):
        user = self.context.get('request').user
        post = attrs.get('post')
        try:
            rating = Review.objects.filter(user=user)
            reviews = Review.objects.filter(post=post)
            # reviews = [reviews[i] for i in range(len(reviews))]
            # reviews = [str(reviews[i]) for i in range(len(reviews))]
            # print(rating, reviews)
            for i in rating:
                if i in reviews:
                    raise serializers.ValidationError('Вы уже оставили отзыв')
            return attrs
        except IndexError:
            return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     validated_data['author'] = user
    #     return super().create(validated_data)


class FavoritesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user']

    user = serializers.EmailField(required=True)

    def validate_user(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate(self, attrs):
        user = attrs.get('user')
        favorites_queryset = Favorite.objects.filter(user=user)
        favorites_queryset = [favorites_queryset[i] for i in range(len(favorites_queryset))]
        favorites = [str(favorites_queryset[i]) for i in range(len(favorites_queryset))]
        attrs['user'] = favorites
        return attrs


class LikesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['user']

    user = serializers.EmailField(required=True)

    def validate_user(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь не найден')
        return email

    def validate(self, attrs):
        user = attrs.get('user')
        likes_queryset = Like.objects.filter(user=user)
        likes_queryset = [likes_queryset[i] for i in range(len(likes_queryset))]
        likes = [str(likes_queryset[i]) for i in range(len(likes_queryset))]
        attrs['user'] = likes
        return attrs


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['image']


class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['video']


class PostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(allow_empty_file=False),
                                   write_only=True,
                                   required=False)
    videos = serializers.ListField(child=serializers.FileField(allow_empty_file=False),
                                  write_only=True,
                                  required=False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'category', 'reviews', 'images', 'videos', 'created_at']

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['user'] = user
        images = validated_data.pop('images', [])
        videos = validated_data.pop('videos', [])
        post = super().create(validated_data)
        for video in videos:
            PostVideo.objects.create(post=post, video=video)
        for image in images:
            PostImage.objects.create(post=post, image=image)
        send_new_series.delay()
        return post

    def update(self, instance, validated_data):
        images = validated_data.pop('images', [])
        videos = validated_data.pop('videos', [])
        if images:
            for image in images:
                PostImage.objects.create(post=instance, image=image)
        if videos:
            for video in videos:
                PostVideo.objects.create(post=instance, video=video)
        return super().update(instance, validated_data)

    def is_favorited(self, post):
        user = self.context.get('request').user
        return user.favorited.filter(post=post).exists()

    def is_liked(self, post):
        user = self.context.get('request').user
        return user.liked.filter(post=post).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['images'] = PostImageSerializer(instance.pics.all(), many=True).data
        representation['videos'] = PostVideoSerializer(instance.trailer.all(), many=True).data
        representation['reviews'] = ReviewSerializer(instance.reviews.all(), many=True).data
        user = self.context.get('request').user
        if user.is_authenticated:
            representation['is_favorited'] = self.is_favorited(instance)
            representation['is_liked'] = self.is_liked(instance)
        representation['likes_count'] = instance.likes.count()
        rating = ReviewSerializer(instance.reviews.all(), many=True).data
        try:
            fl = 0
            for ordered_dict in rating:
                fl += ordered_dict.get('rating')
            representation['rating_average'] = round(fl / instance.reviews.all().count(), 1)
            return representation
        except ZeroDivisionError:
            return representation


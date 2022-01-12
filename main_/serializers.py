from rest_framework import serializers

from main_.models import Category, Post, PostImage, PostVideo, Review


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
        fields = ['id', 'title', 'text', 'category', 'reviews', 'created_at', 'user', 'image', 'video']

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

    def is_liked(self, post):
        user = self.context.get('request').user
        return user.liked.filter(post=post).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user
        if user.is_authenticated:
            representation['is_liked'] = self.is_liked(instance)
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(),
                                              write_only=True)

    class Meta:
        model = Review
        exclude = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    # def create(self, validated_data):
    #     user = self.context['request'].user
    #     validated_data['author'] = user
    #     return super().create(validated_data)


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
        # exclude = ['user', ]
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
            representation['is_liked'] = self.is_liked(instance)
        representation['likes_count'] = instance.favorites.count()
        return representation


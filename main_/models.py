from django.contrib.auth import get_user_model
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(primary_key=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='pics')
    image = models.ImageField(upload_to='posts')


class PostVideo(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='trailer')
    video = models.FileField(upload_to='posts')


class Review(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='reviews')
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Favorites(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='liked')

    class Meta:
        unique_together = ['post', 'user']

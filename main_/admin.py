from django.contrib import admin

from .models import Category, Post, PostImage, PostVideo, Review


class PostImageInline(admin.TabularInline):
    model = PostImage
    fields = ['image']


class PostVideoInline(admin.TabularInline):
    model = PostVideo
    fields = ['video']


class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInline, PostVideoInline]


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Review)

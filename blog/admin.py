from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'post_image',
        'title',
        'category',
        'is_published',
        'created_at',
    )

    list_filter = (
        'category',
        'is_published',
        'created_at',
    )

    search_fields = (
        'title',
        'short_description',
        'content',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    readonly_fields = (
        'created_at',
    )

    fieldsets = (
        ("Post Information", {
            'fields': (
                'title',
                'slug',
                'category',
                'is_published',
            )
        }),

        ("Post Content", {
            'fields': (
                'short_description',
                'content',
                'image',
            )
        }),

        ("System Info", {
            'fields': (
                'created_at',
            )
        }),
    )

    def post_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;" />',
                obj.image.url
            )
        return "—"

    post_image.short_description = "Image"

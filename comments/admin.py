from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'parent', 'created_at')
    list_filter = ('created_at', 'course')
    search_fields = ('user__username', 'course__title', 'content')
    readonly_fields = ('created_at',)
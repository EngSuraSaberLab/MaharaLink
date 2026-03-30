from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from blog.models import Post


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.course:
            return f"{self.user.username} - {self.course.title}"
        if self.post:
            return f"{self.user.username} - {self.post.title}"
        return f"{self.user.username} - Comment"
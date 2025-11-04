from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
from django.db.models import Q

from blogPlatform.comments.managers import CommentManager
from blogPlatform.common.models import BaseModel


User = get_user_model()


class Comment(BaseModel):
    """Comment model for user comments on articles"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True
    )
    text = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(2)],
        db_index=True
    )

    objects = CommentManager()

    class Meta:
        db_table = 'article_comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['user', 'created_at']),

            models.Index(fields=['article', 'is_deleted', 'created_at']),
            models.Index(fields=['user', 'is_deleted', 'created_at']),
            models.Index(fields=['article', 'user', 'created_at']),

            models.Index(
                fields=['article', 'created_at'],
                name='idx_active_comments_chronological',
                condition=Q(is_deleted=False)
            ),
        ]

    def __str__(self):
        status = "deleted" if self.is_deleted else "active"
        return f"Comment by {self.user.username} ({status})"

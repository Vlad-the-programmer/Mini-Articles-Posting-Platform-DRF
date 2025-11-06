from django.db import models
from django.contrib.auth import get_user_model

from common.models import BaseModel
from likes.managers import LikeManager


User = get_user_model()


class Like(BaseModel):
    """Like model for user likes on articles"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True
    )
    article = models.ForeignKey(
        "articles.Article",
        on_delete=models.CASCADE,
        related_name='likes',
        db_index=True
    )

    objects = LikeManager()

    class Meta:
        db_table = 'article_likes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['article', 'created_at']),

            models.Index(fields=['user', 'article', 'is_deleted']),
            models.Index(fields=['article', 'is_deleted', 'created_at']),

            models.Index(
                fields=['article'],
                name='idx_active_likes_per_article',
                condition=models.Q(is_deleted=False)
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'article'],
                name='unique_user_article_like',
                condition=models.Q(is_deleted=False)  # Only enforce for active likes
            )
        ]

    def __str__(self):
        status = "deleted" if self.is_deleted else "active"
        return f"{self.user.username} likes {self.article.title} ({status})"

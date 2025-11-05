from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model

from blogPlatform.common.models import BaseModel
from .managers import ArticleManager


User = get_user_model()


class Article(BaseModel):
    """Article model representing blog posts"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        db_index=True
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        db_index=True
    )
    content = models.TextField(
        validators=[MinLengthValidator(50)]
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Comma-separated tags"),
        db_index=True
    )
    is_published = models.BooleanField(default=True, db_index=True)

    objects = ArticleManager()

    class Meta:
        db_table = 'articles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['is_published', 'created_at']),
            models.Index(fields=['tags', 'is_published']),
            models.Index(
                fields=['title'],
                name='idx_article_title_active',
                condition=models.Q(is_deleted=False, is_published=True)
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title',
                condition=models.Q(is_deleted=False)  # Only enforce uniqueness for active records
            )
        ]

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        """Return tags as list"""
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []

    def get_likes_count(self):
        """Get number of likes for this article"""
        return self.likes.count()

    def get_comments_count(self):
        """Get number of comments for this article"""
        return self.comments.count()

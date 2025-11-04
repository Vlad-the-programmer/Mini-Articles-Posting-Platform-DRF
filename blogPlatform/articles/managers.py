from django.db import models

from blogPlatform.common.managers import SoftDeleteManager


class ArticleManager(SoftDeleteManager):
    """Custom manager for Article model with common queries"""

    def published(self):
        """Return only published articles"""
        return self.filter(is_published=True)

    def with_likes_count(self):
        """Annotate articles with likes count"""
        return self.annotate(likes_count=models.Count('likes'))


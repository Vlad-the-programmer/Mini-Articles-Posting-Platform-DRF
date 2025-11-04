from blogPlatform.common.managers import SoftDeleteManager


class CommentManager(SoftDeleteManager):
    """Custom manager for Comment model"""

    def for_article(self, article):
        """Return comments for specific article (non-deleted)"""
        return self.filter(article=article, is_deleted=False)

    def by_user(self, user):
        """Return comments by specific user (non-deleted)"""
        return self.filter(user=user, is_deleted=False)
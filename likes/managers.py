from common.managers import SoftDeleteManager


class LikeManager(SoftDeleteManager):
    """Custom manager for Like model"""

    def for_user(self, user):
        """Return user's likes (non-deleted)"""
        return self.filter(user=user, is_deleted=False)

    def for_article(self, article):
        """Return likes for article (non-deleted)"""
        return self.filter(article=article, is_deleted=False)
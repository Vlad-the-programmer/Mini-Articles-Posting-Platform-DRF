from django_filters import rest_framework as filters
from .models import Comment


class CommentFilter(filters.FilterSet):
    """FilterSet for comments"""
    article = filters.NumberFilter(field_name='article_id', help_text="Filter by article ID")
    user = filters.NumberFilter(field_name='user_id', help_text="Filter by user ID")
    username = filters.CharFilter(
        field_name='user__username',
        lookup_expr='iexact',
        help_text="Filter by username (case-insensitive exact match)"
    )

    class Meta:
        model = Comment
        fields = ['article', 'user', 'username']

    @property
    def qs(self):
        """Ensure we only return non-deleted comments"""
        return super().qs.filter(is_deleted=False)
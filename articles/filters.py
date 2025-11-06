from django_filters import rest_framework as filters
from .models import Article


class ArticleFilter(filters.FilterSet):
    """FilterSet for articles"""
    tags = filters.CharFilter(method='filter_tags')
    author = filters.CharFilter(field_name='author__username', lookup_expr='iexact')
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ['author', 'tags', 'title']

    def filter_tags(self, queryset, name, value):
        """Filter by tags (comma-separated)"""
        if value:
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            for tag in tags:
                queryset = queryset.filter(tags__icontains=tag)
        return queryset


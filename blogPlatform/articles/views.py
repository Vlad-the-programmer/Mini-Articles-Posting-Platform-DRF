from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Count

from .models import Article
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer
)
from .filters import ArticleFilter
from .permissions import IsArticleOwner


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing articles.

    - Anyone can list and retrieve articles
    - Authenticated users can create articles
    - Only article owners can update/delete their articles
    """
    queryset = Article.objects.with_likes_count().select_related('author')
    permission_classes = [IsAuthenticatedOrReadOnly, IsArticleOwner]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'likes_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ArticleCreateUpdateSerializer
        return ArticleDetailSerializer

    def get_queryset(self):
        """Optimize queryset based on action"""
        queryset = super().get_queryset()

        # Prefetch related data for detail view
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('comments', 'likes')

        return queryset

    def perform_create(self, serializer):
        """Set the author to the current user when creating"""
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        """List articles with optimized queryset"""
        queryset = self.filter_queryset(self.get_queryset())

        # Annotate with counts for list view
        queryset = queryset.annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve article with counts"""
        instance = self.get_object()

        # Manually add counts to instance for serializer
        instance.likes_count = instance.get_likes_count()
        instance.comments_count = instance.get_comments_count()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

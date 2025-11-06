from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    extend_schema_serializer
)
from drf_spectacular.types import OpenApiTypes

from django.db.models import Count

from .models import Article
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleUpdateSerializer,
    ArticleCreateSerializer
)
from .filters import ArticleFilter
from .permissions import IsArticleOwner


@extend_schema_view(
    list=extend_schema(
        summary="List all published articles",
        description="""
        Retrieve a paginated list of all published articles.

        **Features**:
        - Filtering by author, tags, and title
        - Search across title, content, and tags
        - Ordering by creation date, update date, or likes count
        - Pagination (default: 3 items per page)

        **Permissions**: Public endpoint - no authentication required
        """,
        parameters=[
            OpenApiParameter(
                name='author',
                description='Filter by author username (exact match)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='tags',
                description='Filter by tags (comma-separated)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='title',
                description='Filter by title (case-insensitive contains)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='search',
                description='Search in title, content, and tags',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='ordering',
                description='Which field to use when ordering the results',
                required=False,
                type=str,
                enum=['created_at', '-created_at', 'updated_at', '-updated_at', 'likes_count', '-likes_count']
            ),
        ],
        responses={
            200: ArticleListSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'Success Response Example',
                value={
                    "count": 12,
                    "next": "http://localhost:8000/api/articles/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Getting Started with Django",
                            "excerpt": "A comprehensive guide to Django...",
                            "author": {
                                "id": 1,
                                "username": "johndoe",
                                "email": "john@example.com"
                            },
                            "tags": "django,web-development,python",
                            "likes_count": 15,
                            "comments_count": 8,
                            "created_at": "2023-01-15T10:30:00Z",
                            "updated_at": "2023-01-16T14:20:00Z"
                        }
                    ]
                },
                response_only=True
            )
        ],
        tags=['Articles']
    ),
    retrieve=extend_schema(
        summary="Retrieve article details",
        description="""
        Get complete details of a specific published article.

        Includes:
        - Full article content
        - Author information
        - Comments and likes data
        - Real-time counts

        **Permissions**: Public endpoint - no authentication required
        """,
        responses={
            200: ArticleDetailSerializer,
            404: OpenApiResponse(description="Article not found or not published")
        },
        tags=['Articles']
    ),
    create=extend_schema(
        summary="Create a new article",
        description="""
        Create a new article. The authenticated user will be set as the author.

        **Validation Rules**:
        - Title: minimum 5 characters
        - Content: minimum 50 characters
        - Tags: maximum 10 tags, each tag max 50 characters

        **Permissions**: Only authenticated users can create articles
        """,
        request=ArticleCreateSerializer,
        responses={
            201: ArticleDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided")
        },
        examples=[
            OpenApiExample(
                'Create Article Request',
                value={
                    "title": "My First Django Article",
                    "content": "This is a comprehensive guide about Django REST Framework with detailed content that exceeds the minimum 50 character requirement.",
                    "tags": "django,rest-framework,api"
                },
                request_only=True
            )
        ],
        tags=['Articles']
    ),
    update=extend_schema(
        summary="Update entire article",
        description="""
        Replace all article fields. All required fields must be provided.

        **Permissions**: Only the article owner can update
        """,
        request=ArticleUpdateSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not the article owner"),
            404: OpenApiResponse(description="Article not found")
        },
        tags=['Articles']
    ),
    partial_update=extend_schema(
        summary="Partially update article",
        description="""
        Update specific fields of an article. Only provided fields will be updated.

        **Permissions**: Only the article owner can update
        """,
        request=ArticleUpdateSerializer,
        responses={
            200: ArticleDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not the article owner"),
            404: OpenApiResponse(description="Article not found")
        },
        tags=['Articles']
    ),
    destroy=extend_schema(
        summary="Delete article",
        description="""
        Permanently delete an article.

        **Note**: This action cannot be undone.

        **Permissions**: Only the article owner can delete
        """,
        responses={
            204: OpenApiResponse(description="Article deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not the article owner"),
            404: OpenApiResponse(description="Article not found")
        },
        tags=['Articles']
    )
)
class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for comprehensive article management.

    Provides full CRUD operations for blog articles with advanced features:

    **Key Features**:
    - Public read access for published articles
    - Authenticated users can create articles
    - Article owners have full edit/delete permissions
    - Advanced filtering, searching, and ordering
    - Optimized queries with counts and related data

    **Permissions**:
    - `IsAuthenticatedOrReadOnly`: Anyone can read, only authenticated users can write
    - `IsArticleOwner`: Only article authors can update/delete their articles

    **Filtering & Search**:
    - Filter by: author, tags, title
    - Search in: title, content, tags
    - Order by: creation date, update date, likes count
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsArticleOwner]
    filterset_class = ArticleFilter
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'likes_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action == 'create':
            return ArticleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ArticleUpdateSerializer
        return ArticleDetailSerializer

    def get_queryset(self):
        """Optimize queryset based on action"""
        # Incl published articles only
        queryset = Article.objects.filter(is_published=True)

        # Apply likes count annotation
        queryset = queryset.annotate(likes_count=Count('likes', distinct=True))

        queryset = queryset.select_related('author')

        # Prefetch related data for detail view
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('comments', 'comments__author', 'likes')

        return queryset

    @extend_schema(
        summary="List articles with counts",
        description="""
        Enhanced list endpoint with additional counts annotation.
        This is the default list action with optimized performance.
        """,
        responses={200: ArticleListSerializer(many=True)},
        tags=['Articles']
    )
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

    @extend_schema(
        summary="Retrieve article with enhanced data",
        description="""
          Get detailed article information including real-time counts
          and prefetched related data (comments, likes).
          """,
        responses={200: ArticleDetailSerializer},
        tags=['Articles']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve article with counts"""
        instance = self.get_object()

        # Manually add counts to instance for serializer
        instance.likes_count = instance.get_likes_count()
        instance.comments_count = instance.get_comments_count()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse
)
from drf_spectacular.types import OpenApiTypes

from .models import Comment
from .serializers import (
    CommentCreateSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
    CommentUpdateSerializer
)
from .permissions import IsCommentOwnerOrArticleOwner
from .filters import CommentFilter



@extend_schema_view(
    list=extend_schema(
        summary="List comments",
        description="""
        Retrieve a list of all non-deleted comments.

        **Features**:
        - Filter by article or user
        - Order by creation date (newest first by default)
        - Pagination support

        **Permissions**: Public endpoint - no authentication required
        """,
        parameters=[
            OpenApiParameter(
                name='article',
                description='Filter comments by article ID',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='user',
                description='Filter comments by user ID',
                required=False,
                type=int
            ),
        ],
        responses={
            200: CommentListSerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'Success Response Example',
                value={
                    "count": 5,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "text": "Great article!",
                            "user": {
                                "id": 1,
                                "username": "johndoe",
                                "email": "john@example.com"
                            },
                            "article": 1,
                            "created_at": "2023-01-15T10:30:00Z",
                            "updated_at": "2023-01-15T10:30:00Z"
                        }
                    ]
                },
                response_only=True
            )
        ],
        tags=['Comments']
    ),
    retrieve=extend_schema(
        summary="Retrieve comment details",
        description="""
        Get complete details of a specific comment.

        **Permissions**: Public endpoint - no authentication required
        """,
        responses={
            200: CommentDetailSerializer,
            404: OpenApiResponse(description="Comment not found")
        },
        tags=['Comments']
    ),
    create=extend_schema(
        summary="Create a new comment",
        description="""
        Create a new comment on an article.

        **Validation Rules**:
        - Text: minimum 2 characters, maximum 1000 characters

        **Permissions**: Only authenticated users can create comments
        """,
        request=CommentCreateSerializer,
        responses={
            201: CommentDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided")
        },
        examples=[
            OpenApiExample(
                'Create Comment Request',
                value={
                    "article": 1,
                    "text": "This is a great article! Very informative."
                },
                request_only=True
            )
        ],
        tags=['Comments']
    ),
    update=extend_schema(
        summary="Update comment",
        description="""
        Update a comment. Only the comment owner can update their comments.

        **Permissions**: Only the comment owner can update
        """,
        request=CommentUpdateSerializer,
        responses={
            200: CommentDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not the comment owner"),
            404: OpenApiResponse(description="Comment not found")
        },
        tags=['Comments']
    ),
    partial_update=extend_schema(
        summary="Partially update comment",
        description="""
        Update specific fields of a comment. Only provided fields will be updated.

        **Permissions**: Only the comment owner can update
        """,
        request=CommentUpdateSerializer,
        responses={
            200: CommentDetailSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not the comment owner"),
            404: OpenApiResponse(description="Comment not found")
        },
        tags=['Comments']
    ),
    destroy=extend_schema(
        summary="Delete comment",
        description="""
        Soft delete a comment. 

        **Permissions**: 
        - Comment owner can delete their comments
        - Article owner can delete any comment on their article
        """,
        responses={
            204: OpenApiResponse(description="Comment deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Not authorized to delete this comment"),
            404: OpenApiResponse(description="Comment not found")
        },
        tags=['Comments']
    )
)
class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on articles.

    Provides full CRUD operations for comments with ownership-based permissions.

    **Key Features**:
    - Public read access for all comments
    - Authenticated users can create comments
    - Comment owners can update their comments
    - Comment owners AND article owners can delete comments
    - Soft deletion (comments are marked as deleted but remain in database)

    **Permissions**:
    - `IsAuthenticatedOrReadOnly`: Anyone can read, only authenticated users can write
    - `IsCommentOwnerOrArticleOwner`: Comment owners can update, both comment and article owners can delete
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwnerOrArticleOwner]
    filterset_class = CommentFilter
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return CommentListSerializer
        elif self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentDetailSerializer

    def get_queryset(self):
        """Return only non-deleted comments with optimized queries"""
        queryset = Comment.objects.select_related('user', 'article')

        # Prefetch related data for detail view
        if self.action == 'retrieve':
            queryset = queryset.select_related('article__author')

        return queryset

    def perform_create(self, serializer):
        """Set the current user as comment author"""
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Get comments for specific article",
        description="""
        Retrieve all comments for a specific article.
        This is a convenience endpoint that filters comments by article ID.
        """,
        parameters=[
            OpenApiParameter(
                name='article_id',
                description='Article ID to filter comments',
                required=True,
                type=int,
                location=OpenApiParameter.PATH
            )
        ],
        responses={
            200: CommentListSerializer(many=True),
            404: OpenApiResponse(description="Article not found")
        },
        tags=['Comments']
    )
    @action(detail=False, methods=['get'], url_path='article/(?P<article_id>\d+)')
    def by_article(self, request, article_id=None):
        """Get all comments for a specific article"""
        from articles.models import Article

        # Verify article exists and is published
        try:
            article = Article.objects.published().get(id=article_id)
        except Article.DoesNotExist:
            return Response(
                {"detail": "Article not found or not published"},
                status=status.HTTP_404_NOT_FOUND
            )

        comments = Comment.objects.for_article(article)
        page = self.paginate_queryset(comments)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get current user's comments",
        description="""
        Retrieve all comments made by the currently authenticated user.
        """,
        responses={
            200: CommentListSerializer(many=True),
            401: OpenApiResponse(description="Authentication required")
        },
        tags=['Comments']
    )
    @action(detail=False, methods=['get'])
    def current_user_comments(self, request):
        """Get all comments by the current user"""
        comments = Comment.objects.by_user(request.user)
        page = self.paginate_queryset(comments)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from .models import Like
from .serializers import LikeSerializer, LikeToggleSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List user's likes",
        description="Retrieve a list of all articles that the current user has liked.",
        responses={
            200: LikeSerializer(many=True),
            401: OpenApiResponse(description="Authentication credentials were not provided.")
        },
        tags=['Likes']
    ),
    retrieve=extend_schema(
        summary="Retrieve a like",
        description="Get details about a specific like by its ID.",
        responses={
            200: LikeSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Like not found.")
        },
        tags=['Likes']
    ),
    create=extend_schema(
        summary="Like an article",
        description="Create a new like for an article. Returns 400 if already liked.",
        request=LikeToggleSerializer,
        responses={
            201: LikeSerializer,
            400: OpenApiResponse(description="Already liked this article."),
            401: OpenApiResponse(description="Authentication credentials were not provided.")
        },
        examples=[
            OpenApiExample(
                'Like Request Example',
                value={'article_id': 1},
                request_only=True
            )
        ],
        tags=['Likes']
    ),
    destroy=extend_schema(
        summary="Unlike an article",
        description="Remove a like by its ID. Users can only remove their own likes.",
        responses={
            204: OpenApiResponse(description="Like removed successfully."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            403: OpenApiResponse(description="Not authorized to remove this like."),
            404: OpenApiResponse(description="Like not found.")
        },
        tags=['Likes']
    )
)
class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing likes on articles.

    Provides endpoints for:
    - Listing user's liked articles
    - Liking articles
    - Unliking articles
    - Toggling likes

    **Permissions**:
    - Only authenticated users can access these endpoints
    - Users can only manage their own likes

    **Business Logic**:
    - Users can only like each article once
    - Likes are soft-deleted when removed
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Only allow these methods

    def get_serializer_class(self):
        if self.action in ['create', 'destroy', 'toggle']:
            return LikeToggleSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """Return only current user's likes"""
        return Like.objects.filter(user=self.request.user).select_related('article', 'user')

    @extend_schema(
        summary="Toggle like for an article",
        description="""
        Toggle like status for an article. 
        - If article is not liked, creates a new like
        - If article is already liked, removes the like

        This is a convenient alternative to separate create/delete operations.
        """,
        request=LikeToggleSerializer,
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Like removed",
                examples=[
                    OpenApiExample(
                        "Unlike Response",
                        value={
                            "detail": "Like removed",
                            "liked": False
                        }
                    )
                ]
            ),
            201: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Like added",
                examples=[
                    OpenApiExample(
                        "Like Response",
                        value={
                            "detail": "Like added",
                            "liked": True,
                            "like": {
                                "id": 1,
                                "article": 1,
                                "user": 1,
                                "created_at": "2023-01-01T12:00:00Z"
                            }
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description="Authentication credentials were not provided.")
        },
        examples=[
            OpenApiExample(
                'Toggle Like Request',
                value={'article_id': 1},
                request_only=True
            )
        ],
        tags=['Likes']
    )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle like for an article"""
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data['article_id']

        # Try to get existing like
        like = Like.objects.filter(
            user=request.user,
            article_id=article_id
        ).first()

        if like:
            # Unlike - soft delete the like
            like.delete()
            return Response(
                {"detail": "Like removed", "liked": False},
                status=status.HTTP_200_OK
            )
        else:
            # Like - create new like
            like = Like.objects.create(
                user=request.user,
                article_id=article_id
            )
            return Response(
                {
                    "detail": "Like added",
                    "liked": True,
                    "like_id": like.id,
                    "article_id": like.article_id,
                    "user_id": like.user_id,
                    "created_at": like.created_at
                },
                status=status.HTTP_201_CREATED
            )

    def create(self, request, *args, **kwargs):
        """Like an article"""
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data['article_id']

        # Check if like already exists
        like, created = Like.objects.get_or_create(
            user=request.user,
            article_id=article_id,
            defaults={'user': request.user, 'article_id': article_id}
        )

        if created:
            # Like was created
            return Response(
                {
                    "detail": "Like added",
                    "like_id": like.id,
                    "article_id": like.article_id,
                    "user_id": like.user_id,
                    "created_at": like.created_at
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # Like already exists
            return Response(
                {"detail": "You have already liked this article"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Unlike an article by like ID"""
        like = self.get_object()

        # Ensure user can only delete their own likes
        if like.user != request.user:
            return Response(
                {"detail": "You can only remove your own likes"},
                status=status.HTTP_403_FORBIDDEN
            )

        like.delete()
        return Response(
            {"detail": "Like removed"},
            status=status.HTTP_204_NO_CONTENT
        )
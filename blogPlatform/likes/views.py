from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Like
from .serializers import LikeSerializer, LikeToggleSerializer


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing likes.

    - Authenticated users can like/unlike articles
    - Users can only like each article once
    - Users can only manage their own likes
    """
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']  # Only allow these methods

    def get_queryset(self):
        """Return only current user's likes"""
        return Like.objects.filter(user=self.request.user).select_related('article', 'user')

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
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Like already exists
            return Response(
                {"detail": "You have already liked this article"},
                status=status.HTTP_400_BAD_REQUEST
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
            serializer = self.get_serializer(like)
            return Response(
                {"detail": "Like added", "liked": True, "like": serializer.data},
                status=status.HTTP_201_CREATED
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
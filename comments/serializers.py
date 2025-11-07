from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Comment

User = get_user_model()


class CommentUserSerializer(serializers.ModelSerializer):
    """Serializer for comment author information"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = fields


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Comment List Example',
            value={
                'id': 1,
                'text': 'Great article! Very informative.',
                'user': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com'
                },
                'article': 1,
                'created_at': '2023-01-15T10:30:00Z',
                'updated_at': '2023-01-15T10:30:00Z'
            },
            response_only=True
        )
    ]
)
class CommentListSerializer(serializers.ModelSerializer):
    """Serializer for comment listing"""
    user = CommentUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'user', 'article', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Comment Detail Example',
            value={
                'id': 1,
                'text': 'Great article! Very informative.',
                'user': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com'
                },
                'article': 1,
                'created_at': '2023-01-15T10:30:00Z',
                'updated_at': '2023-01-15T10:30:00Z',
                'is_owner': True,
                'can_delete': True
            },
            response_only=True
        )
    ]
)
class CommentDetailSerializer(serializers.ModelSerializer):
    """Serializer for comment detail view"""
    user = CommentUserSerializer(read_only=True)
    is_owner = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'user', 'article', 'created_at', 'updated_at', 'is_owner', 'can_delete')
        read_only_fields = ('id', 'user', 'article', 'created_at', 'updated_at')

    def get_is_owner(self, obj):
        """Check if current user is the comment owner"""
        request = self.context.get('request')
        return request and request.user == obj.user

    def get_can_delete(self, obj) -> bool:
        """Check if current user can delete this comment"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user == obj.user or request.user == obj.article.author


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create Comment Request',
            value={
                'article': 1,
                'text': 'This is a great article! Very informative.'
            },
            request_only=True
        )
    ]
)
class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""

    class Meta:
        model = Comment
        fields = ('article', 'text')
        extra_kwargs = {
            'text': {
                'min_length': 2,
                'max_length': 1000,
                'help_text': 'Comment text (2-1000 characters)'
            }
        }

    def validate_article(self, value):
        """Validate that article exists and is published"""
        if not value.is_published:
            raise serializers.ValidationError("Cannot comment on unpublished articles")
        return value


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Update Comment Request',
            value={
                'text': 'Updated comment text with more details.'
            },
            request_only=True
        )
    ]
)
class CommentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating comments"""

    class Meta:
        model = Comment
        fields = ('text',)
        extra_kwargs = {
            'text': {
                'min_length': 2,
                'max_length': 1000,
                'required': False,
                'help_text': 'Comment text (2-1000 characters)'
            }
        }
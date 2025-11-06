from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import Article

User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Author Example',
            value={
                'id': 1,
                'username': 'johndoe',
                'email': 'john@example.com'
            },
            response_only=True
        )
    ]
)
class ArticleAuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for article author information.

    Provides minimal user details for article representations.
    Used in list and detail views to display author information.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = fields


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Article List Example',
            value={
                'id': 1,
                'title': 'Getting Started with Django REST Framework',
                'author': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com'
                },
                'created_at': '2023-01-15T10:30:00Z',
                'updated_at': '2023-01-16T14:20:00Z',
                'tags': 'django,rest-framework,api',
                'tag_list': ['django', 'rest-framework', 'api'],
                'is_published': True,
                'likes_count': 15,
                'comments_count': 8
            },
            response_only=True
        )
    ]
)
class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializer for article listing (optimized for lists).

    Provides a lightweight representation of articles for list views
    with essential information and counts for display in article grids
    or summary lists.

    **Fields**:
    - Basic article metadata (title, dates, publication status)
    - Author information (nested object)
    - Engagement metrics (likes and comments counts)
    - Tags in both string and list formats
    """
    author = ArticleAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of likes the article has received"
    )
    comments_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of comments on the article"
    )
    tag_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Tags as a list for easier frontend processing"
    )

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'author', 'created_at', 'updated_at',
            'tags', 'tag_list', 'is_published', 'likes_count', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'author')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Article Detail Example',
            value={
                'id': 1,
                'title': 'Getting Started with Django REST Framework',
                'content': 'This is a comprehensive guide about Django REST Framework...',
                'author': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com'
                },
                'created_at': '2023-01-15T10:30:00Z',
                'updated_at': '2023-01-16T14:20:00Z',
                'tags': 'django,rest-framework,api',
                'tag_list': ['django', 'rest-framework', 'api'],
                'is_published': True,
                'likes_count': 15,
                'comments_count': 8,
                'is_owner': False
            },
            response_only=True
        )
    ]
)
class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for article detail view.

    Provides complete article information including full content
    and ownership information for detailed article pages.

    **Fields**:
    - Complete article content and metadata
    - Author information
    - Engagement metrics
    - Ownership flag for UI controls
    - Tags in multiple formats
    """
    author = ArticleAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of likes the article has received"
    )
    comments_count = serializers.IntegerField(
        read_only=True,
        help_text="Number of comments on the article"
    )
    tag_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="Tags as a list for easier frontend processing"
    )
    is_owner = serializers.SerializerMethodField(
        help_text="True if the current user is the article author"
    )

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'content', 'author', 'created_at', 'updated_at',
            'tags', 'tag_list', 'is_published', 'likes_count', 'comments_count', 'is_owner'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'author')

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_owner(self, obj: Article) -> bool:
        """Check if current user is the article owner"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Create Article Request',
            summary="Create a new article",
            description="Example request for creating a new article",
            value={
                'title': 'My First Django Article',
                'content': 'This is a comprehensive guide about Django REST Framework with detailed content that exceeds the minimum 50 character requirement.',
                'tags': 'django,rest-framework,api'
            },
            request_only=True
        ),
        OpenApiExample(
            'Create Article Response',
            summary="Created article response",
            description="Response after successfully creating an article",
            value={
                'id': 1,
                'title': 'My First Django Article',
                'content': 'This is a comprehensive guide about Django REST Framework with detailed content that exceeds the minimum 50 character requirement.',
                'tags': 'django,rest-framework,api'
            },
            response_only=True
        )
    ]
)
class ArticleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new articles.

    Used exclusively for article creation with strict validation
    and automatic author assignment.

    **Validation Rules**:
    - Title: Minimum 5 characters, required
    - Content: Minimum 50 characters, required
    - Tags: Maximum 10 tags, each tag max 50 characters

    **Auto-assigned**:
    - Author: Set to current authenticated user
    - ID: Auto-generated upon creation
    """

    class Meta:
        model = Article
        fields = ('title', 'content', 'tags', 'id')
        read_only_fields = ('id',)
        extra_kwargs = {
            'title': {
                'min_length': 5,
                'help_text': 'Article title (min 5 characters)'
            },
            'content': {
                'min_length': 50,
                'help_text': 'Article content (min 50 characters)'
            },
            'tags': {
                'help_text': 'Comma-separated tags (max 10 tags, each max 50 chars)'
            },
        }

    def validate_tags(self, value):
        """
        Validate tags format and constraints.

        Rules:
        - Maximum 10 tags allowed
        - Each tag maximum 50 characters
        - Tags are comma-separated
        - Whitespace around tags is trimmed
        """
        if value:
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            if len(tags) > 10:
                raise serializers.ValidationError("Maximum 10 tags allowed")
            for tag in tags:
                if len(tag) > 50:
                    raise serializers.ValidationError(f"Tag '{tag}' is too long (max 50 characters)")
        return value

    def create(self, validated_data):
        """
        Create article with current user as author.

        Automatically assigns the authenticated user as the article author
        and creates the article record in the database.
        """
        user = self.context['request'].user
        return Article.objects.create(author=user, **validated_data)


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Update Article Request - Full',
            summary="Full update request",
            description="Update all article fields (PUT)",
            value={
                'title': 'Updated Article Title',
                'content': 'This is the updated content with at least 50 characters to pass validation requirements.',
                'tags': 'updated,django,api'
            },
            request_only=True
        ),
        OpenApiExample(
            'Update Article Request - Partial',
            summary="Partial update request",
            description="Update only specific fields (PATCH)",
            value={
                'title': 'Only Updating The Title'
            },
            request_only=True
        ),
        OpenApiExample(
            'Update Article Response',
            summary="Update response",
            description="Response after successful update",
            value={
                'id': 1,
                'title': 'Updated Article Title',
                'content': 'This is the updated content...',
                'author': {
                    'id': 1,
                    'username': 'johndoe',
                    'email': 'john@example.com'
                },
                'tags': 'updated,django,api',
                'tag_list': ['updated', 'django', 'api'],
                'is_published': True,
                'likes_count': 15,
                'comments_count': 8,
                'is_owner': True,
                'created_at': '2023-01-15T10:30:00Z',
                'updated_at': '2023-01-17T09:15:00Z'
            },
            response_only=True
        )
    ]
)
class ArticleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing articles.

    Designed for both PUT (full update) and PATCH (partial update) operations.
    All fields are optional to support partial updates.

    **Validation Rules** (when provided):
    - Title: Minimum 5 characters
    - Content: Minimum 50 characters
    - Tags: Maximum 10 tags, each tag max 50 characters

    **Note**: Only provided fields are updated; omitted fields retain their current values.
    """

    class Meta:
        model = Article
        fields = ('title', 'content', 'tags')
        extra_kwargs = {
            'title': {
                'min_length': 5,
                'required': False,
                'allow_blank': True,
                'help_text': 'Article title (min 5 characters, optional for updates)'
            },
            'content': {
                'min_length': 50,
                'required': False,
                'allow_blank': True,
                'help_text': 'Article content (min 50 characters, optional for updates)'
            },
            'tags': {
                'required': False,
                'allow_blank': True,
                'help_text': 'Comma-separated tags (max 10 tags, each max 50 chars, optional)'
            },
        }

    def validate_tags(self, value):
        """
        Validate tags format and constraints.

        Only validates if tags are provided in the update request.
        Same rules as ArticleCreateSerializer.
        """
        if value:
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            if len(tags) > 10:
                raise serializers.ValidationError("Maximum 10 tags allowed")
            for tag in tags:
                if len(tag) > 50:
                    raise serializers.ValidationError(f"Tag '{tag}' is too long (max 50 characters)")
        return value
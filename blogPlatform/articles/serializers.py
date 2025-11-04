from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Article


User = get_user_model()


class ArticleAuthorSerializer(serializers.ModelSerializer):
    """Serializer for article author information"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = fields


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for article listing (optimized for lists)"""
    author = ArticleAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    tag_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        source='tag_list'
    )

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'author', 'created_at', 'updated_at',
            'tags', 'tag_list', 'is_published', 'likes_count', 'comments_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'author')


class ArticleDetailSerializer(serializers.ModelSerializer):
    """Serializer for article detail view"""
    author = ArticleAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    tag_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        source='tag_list'
    )
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'content', 'author', 'created_at', 'updated_at',
            'tags', 'tag_list', 'is_published', 'likes_count', 'comments_count', 'is_owner'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'author')

    def get_is_owner(self, obj):
        """Check if current user is the article owner"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles"""
    class Meta:
        model = Article
        fields = ('title', 'content', 'tags', 'is_published')
        extra_kwargs = {
            'title': {'min_length': 5},
            'content': {'min_length': 50},
        }

    def validate_tags(self, value):
        """Validate tags format"""
        if value:
            tags = [tag.strip() for tag in value.split(',') if tag.strip()]
            if len(tags) > 10:
                raise serializers.ValidationError("Maximum 10 tags allowed")
            for tag in tags:
                if len(tag) > 50:
                    raise serializers.ValidationError(f"Tag '{tag}' is too long (max 50 characters)")
        return value

    def create(self, validated_data):
        """Create article with current user as author"""
        user = self.context['request'].user
        return Article.objects.create(author=user, **validated_data)
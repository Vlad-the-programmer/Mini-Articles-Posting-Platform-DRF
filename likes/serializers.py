from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from articles.models import Article
from articles.serializers import ArticleAuthorSerializer
from likes.models import Like


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Like Serializer Example',
            value={
                'id': 1,
                'article': 1,
                'user': 1,
                'created_at': '2023-01-01T12:00:00Z'
            },
            response_only=True
        )
    ]
)
class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    user = ArticleAuthorSerializer(read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'article', 'article_title', 'created_at')
        read_only_fields = ('id', 'user', 'created_at', 'article_title')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Toggle Like Request',
            value={'article_id': 1},
            request_only=True
        )
    ]
)
class LikeToggleSerializer(serializers.Serializer):
    """Serializer for like toggle action"""
    article_id = serializers.IntegerField(help_text=_("ID of the article to like"))

    class Meta:
        model = Like
        fields = ('article_id')

    def validate_article_id(self, value):
        """Validate that article exists and is published"""
        try:
            article = Article.objects.published().get(id=value)
        except Article.DoesNotExist:
            raise serializers.ValidationError("Article not found or not published")
        return value

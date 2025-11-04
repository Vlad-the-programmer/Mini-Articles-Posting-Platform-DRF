from rest_framework import serializers

from blogPlatform.articles.models import Article
from blogPlatform.articles.serializers import ArticleAuthorSerializer
from blogPlatform.likes.models import Like


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    user = ArticleAuthorSerializer(read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'user', 'article', 'article_title', 'created_at')
        read_only_fields = ('id', 'user', 'created_at', 'article_title')


class LikeToggleSerializer(serializers.Serializer):
    """Serializer for like toggle action"""
    article_id = serializers.IntegerField()

    def validate_article_id(self, value):
        """Validate that article exists and is published"""
        try:
            article = Article.objects.published().get(id=value)
        except Article.DoesNotExist:
            raise serializers.ValidationError("Article not found or not published")
        return value
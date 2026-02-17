from rest_framework import serializers
from .models import BlogPost, Comment, Like
from rest_framework import serializers
from .models import BlogPost, Comment, Like
# Removed invalid import from users.serializers

class UserSnippetSerializer(serializers.Serializer):
    username = serializers.CharField()
    full_name = serializers.CharField()

class CommentSerializer(serializers.ModelSerializer):
    user = UserSnippetSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class BlogPostListSerializer(serializers.ModelSerializer):
    author = UserSnippetSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'category', 'description', 'image', 'author', 'created_at', 'likes_count', 'is_liked']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = UserSnippetSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'category', 'description', 'image', 'author', 'created_at', 'updated_at', 'likes_count', 'comments', 'is_liked']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

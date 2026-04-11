from rest_framework import serializers
from .models import BlogPost, Comment, Like, Bookmark, Donation


class UserSnippetSerializer(serializers.Serializer):
    username = serializers.CharField()
    full_name = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    user = UserSnippetSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']


class DonationSerializer(serializers.ModelSerializer):
    donor = UserSnippetSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = ['id', 'donor', 'amount', 'transaction_id', 'status', 'created_at']


class BlogPostListSerializer(serializers.ModelSerializer):
    author = UserSnippetSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    total_donations = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'category', 'description', 'image',
            'author', 'created_at', 'likes_count', 'is_liked', 'is_bookmarked',
            'allow_donation', 'total_donations',
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

    def get_total_donations(self, obj):
        return str(obj.total_donations)


class BlogPostDetailSerializer(serializers.ModelSerializer):
    author = UserSnippetSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='total_likes', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    donations = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    total_donations = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'category', 'description', 'image',
            'author', 'created_at', 'updated_at', 'likes_count',
            'comments', 'donations', 'is_liked', 'is_bookmarked',
            'allow_donation', 'total_donations',
        ]

    def get_donations(self, obj):
        completed_donations = obj.donations.filter(status='COMPLETE')
        return DonationSerializer(completed_donations, many=True).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False

    def get_total_donations(self, obj):
        return str(obj.total_donations)

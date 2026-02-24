from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BlogPost, Comment, Like, Bookmark
from .serializers import BlogPostListSerializer, BlogPostDetailSerializer, CommentSerializer
from django.db.models import Count


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.annotate(total_likes=Count('likes')).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action in ['like', 'bookmark', 'comment', 'liked_posts', 'bookmarked_posts']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # ── Like toggle ─────────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        like, created = Like.objects.get_or_create(post=post, user=user)

        if not created:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)

        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)

    # ── Bookmark toggle ──────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        user = request.user

        bookmark, created = Bookmark.objects.get_or_create(post=post, user=user)

        if not created:
            bookmark.delete()
            return Response({'status': 'unbookmarked'}, status=status.HTTP_200_OK)

        return Response({'status': 'bookmarked'}, status=status.HTTP_201_CREATED)

    # ── Liked posts list ─────────────────────────────────────────────────────
    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated],
                       url_path='liked')
    def liked_posts(self, request):
        liked_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        posts = BlogPost.objects.filter(id__in=liked_ids).annotate(
            total_likes=Count('likes')
        ).order_by('-created_at')
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    # ── Bookmarked posts list ────────────────────────────────────────────────
    @decorators.action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated],
                       url_path='bookmarked')
    def bookmarked_posts(self, request):
        bookmarked_ids = Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True)
        posts = BlogPost.objects.filter(id__in=bookmarked_ids).annotate(
            total_likes=Count('likes')
        ).order_by('-created_at')
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    # ── Comment ──────────────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        content = request.data.get('content')

        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(post=post, user=request.user, content=content)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all().order_by('-created_at')
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

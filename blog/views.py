from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import BlogPost, Comment, Like, Bookmark, Donation
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
        if self.action in ['like', 'bookmark', 'comment', 'liked_posts', 'bookmarked_posts', 'donate', 'verify_donation']:
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
            is_liked = False
        else:
            is_liked = True

        return Response({
            'success': True,
            'isLiked': is_liked,
            'total_likes': post.likes.count()
        }, status=status.HTTP_200_OK)

    # ── Bookmark toggle ──────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        post = self.get_object()
        user = request.user

        bookmark, created = Bookmark.objects.get_or_create(post=post, user=user)

        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True

        return Response({
            'success': True,
            'isBookmarked': is_bookmarked
        }, status=status.HTTP_200_OK)

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

    # ── Donate ──────────────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def donate(self, request, pk=None):
        post = self.get_object()
        amount = request.data.get('amount')
        transaction_id = request.data.get('transaction_id')

        if not amount or not transaction_id:
            return Response({'error': 'Amount and transaction_id are required'}, status=status.HTTP_400_BAD_REQUEST)

        if not post.allow_donation:
            return Response({'error': 'This post does not accept donations'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            donation = Donation.objects.create(
                post=post,
                donor=request.user,
                amount=amount,
                transaction_id=transaction_id,
                status='PENDING'
            )
            return Response({
                'success': True,
                'donation_id': donation.id,
                'transaction_id': donation.transaction_id,
                'amount': str(donation.amount),
                'status': donation.status,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ── Verify Donation ───────────────────────────────────────────────────────
    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='verify-donation')
    def verify_donation(self, request, pk=None):
        transaction_id = request.data.get('transaction_id')

        if not transaction_id:
            return Response({'error': 'transaction_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            donation = Donation.objects.get(transaction_id=transaction_id)
            # In a real app we would call eSewa API to verify the transaction.
            # But for sandbox and this demo we just mark it complete.
            donation.status = 'COMPLETE'
            donation.save()
            return Response({'success': True, 'status': 'COMPLETE'}, status=status.HTTP_200_OK)
        except Donation.DoesNotExist:
            return Response({'error': 'Donation not found'}, status=status.HTTP_404_NOT_FOUND)



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

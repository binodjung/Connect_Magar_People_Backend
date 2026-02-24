from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'posts', BlogPostViewSet)
router.register(r'comments', CommentViewSet) # Optional direct access

urlpatterns = [
    path('', include(router.urls)),
]

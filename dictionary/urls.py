from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WordViewSet, WordTranslateView

router = DefaultRouter()
router.register(r'words', WordViewSet, basename='word')

urlpatterns = [
    path('', include(router.urls)),
    path('translate/', WordTranslateView.as_view(), name='word-translate'),
]

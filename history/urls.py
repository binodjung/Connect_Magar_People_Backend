from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HistoryViewSet

router = DefaultRouter()
router.register(r'histories', HistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

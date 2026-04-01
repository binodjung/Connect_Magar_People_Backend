from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizQuestionViewSet

router = DefaultRouter()
router.register(r'questions', QuizQuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

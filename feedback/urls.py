from django.urls import path
from .views import FeedbackSubmissionView

urlpatterns = [
    path("submit/", FeedbackSubmissionView.as_view(), name="feedback-submit"),
]

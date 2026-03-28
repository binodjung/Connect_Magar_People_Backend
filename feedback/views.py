from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FeedbackSerializer
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings

class FeedbackSubmissionView(APIView):
    # Allow anyone to submit feedback even if not logged in
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback = serializer.save()
            
            # Send Email
            try:
                subject = f"New Feedback: {feedback.subject}"
                message = f"You received new feedback from {feedback.email}:\n\n{feedback.message}"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL], # Send it to the admin (user)
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending feedback email: {e}")

            return Response({"message": "Feedback submitted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

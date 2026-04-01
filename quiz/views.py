from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import QuizQuestion
from .serializers import QuizQuestionSerializer

class QuizQuestionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows quiz questions to be viewed or edited.
    """
    queryset = QuizQuestion.objects.all()
    serializer_class = QuizQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally filter questions by category.
        """
        queryset = QuizQuestion.objects.all()
        category = self.request.query_params.get('category')
        if category is not None:
            queryset = queryset.filter(category=category)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if request.query_params.get('random') == 'true':
            # Get 10 random questions bypassing pagination
            queryset = queryset.order_by('?')[:10]
            serializer = self.get_serializer(queryset, many=True)
            return Response({'results': serializer.data})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

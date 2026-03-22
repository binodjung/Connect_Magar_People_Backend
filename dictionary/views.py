from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import Word
from .serializers import WordSerializer

class WordTranslateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        word = request.query_params.get('word', '').strip()
        from_lang = request.query_params.get('from', 'en') # 'en' or 'magar'
        
        if not word:
            return Response({"error": "Word is required"}, status=status.HTTP_400_BAD_REQUEST)

        if from_lang == 'magar':
            # Check for exact magar word
            result = Word.objects.filter(magar_word__iexact=word).first()
            if result:
                return Response({"translation": result.english_meaning})
        else:
            # Check if English meaning contains the word (might be multiple words)
            # or exact match if possible
            result = Word.objects.filter(english_meaning__icontains=word).first()
            if result:
                return Response({"translation": result.magar_word})

        return Response({"message": "Word not found in database"}, status=status.HTTP_404_NOT_FOUND)


class WordPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and retrieve dictionary words.
    Supports:
      - ?search=   — filter by magar_word or english_meaning
      - ?letter=A  — filter words starting with a specific letter
      - ?page=     — pagination (20 per page)
    Always ordered alphabetically by magar_word.
    """
    queryset = Word.objects.all().order_by('magar_word')
    serializer_class = WordSerializer
    permission_classes = [AllowAny]
    pagination_class = WordPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['magar_word', 'english_meaning']

    def get_queryset(self):
        queryset = super().get_queryset()
        letter = self.request.query_params.get('letter', None)
        if letter:
            queryset = queryset.filter(magar_word__istartswith=letter)
        return queryset

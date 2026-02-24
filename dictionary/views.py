from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import Word
from .serializers import WordSerializer


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

from rest_framework import viewsets, permissions
from .models import History
from .serializers import HistoryListSerializer, HistoryDetailSerializer

class HistoryViewSet(viewsets.ModelViewSet):
    queryset = History.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HistoryDetailSerializer
        return HistoryListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

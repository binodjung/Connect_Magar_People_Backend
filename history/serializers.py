from rest_framework import serializers
from .models import History, HistorySection

class HistorySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorySection
        fields = ['id', 'image', 'description', 'order']

class HistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['id', 'title', 'created_at']

class HistoryDetailSerializer(serializers.ModelSerializer):
    sections = HistorySectionSerializer(many=True, read_only=True)

    class Meta:
        model = History
        fields = ['id', 'title', 'sections', 'created_at', 'updated_at']

from rest_framework import serializers
from .models import QuizQuestion

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 
            'question_text', 
            'option1', 
            'option2', 
            'option3', 
            'option4', 
            'correct_option', 
            'category', 
            'created_at', 
            'updated_at'
        ]

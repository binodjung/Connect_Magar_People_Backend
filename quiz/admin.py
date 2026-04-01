from django.contrib import admin
from .models import QuizQuestion

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'category', 'correct_option', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('question_text', 'option1', 'option2', 'option3', 'option4')
    
    fieldsets = (
        ('Question Details', {
            'fields': ('question_text', 'category')
        }),
        ('Options', {
            'fields': ('option1', 'option2', 'option3', 'option4')
        }),
        ('Correct Answer', {
            'fields': ('correct_option',),
            'description': 'Select which option (1-4) is the correct one.'
        }),
    )

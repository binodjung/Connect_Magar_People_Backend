from django.db import models

class QuizQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('language', 'Language'),
        ('culture', 'Culture'),
        ('history', 'History'),
    ]

    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.IntegerField(
        choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')],
        default=1,
        help_text="The index of the correct option (1-4)"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='language')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.category}] {self.question_text[:50]}..."
    
    class Meta:
        ordering = ['-created_at']

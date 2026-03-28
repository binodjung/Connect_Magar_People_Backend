from django.db import models


class Word(models.Model):
    CATEGORY_CHOICES = [
        ('ANIMALS', 'Animals'),
        ('BIRDS', 'Birds'),
        ('FRUITS', 'Fruits'),
        ('COLORS', 'Colors'),
        ('GREETINGS', 'Greetings'),
        ('CITY', 'City'),
        ('OTHERS', 'Others'),
    ]
    magar_word = models.CharField(max_length=200)
    english_meaning = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHERS')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['magar_word']
        verbose_name = 'Dictionary Word'
        verbose_name_plural = 'Dictionary Words'

    def __str__(self):
        return f"[{self.category}] {self.magar_word} — {self.english_meaning[:50]}"

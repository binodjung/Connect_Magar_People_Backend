from django.db import models


class Word(models.Model):
    magar_word = models.CharField(max_length=200)
    english_meaning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['magar_word']
        verbose_name = 'Dictionary Word'
        verbose_name_plural = 'Dictionary Words'

    def __str__(self):
        return f"{self.magar_word} — {self.english_meaning[:60]}"

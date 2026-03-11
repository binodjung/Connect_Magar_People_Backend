from django.db import models

class History(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Histories"

    def __str__(self):
        return self.title

class HistorySection(models.Model):
    history = models.ForeignKey(History, related_name='sections', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='history_images/', null=True, blank=True)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Section {self.order} for {self.history.title}"

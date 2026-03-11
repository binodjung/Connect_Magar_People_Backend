from django.contrib import admin
from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('magar_word', 'english_meaning_short', 'created_at')
    list_display_links = ('magar_word',)
    search_fields = ('magar_word', 'english_meaning')
    ordering = ('magar_word',)
    readonly_fields = ('created_at',)

    def english_meaning_short(self, obj):
        return obj.english_meaning[:80] + '...' if len(obj.english_meaning) > 80 else obj.english_meaning
    english_meaning_short.short_description = 'English Meaning'

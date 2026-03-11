from django.contrib import admin
from .models import History, HistorySection

class HistorySectionInline(admin.StackedInline):
    model = HistorySection
    extra = 1
    sortable_field_name = "order"

class HistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    inlines = [HistorySectionInline]

admin.site.register(History, HistoryAdmin)

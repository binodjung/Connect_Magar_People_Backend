from django.contrib import admin
from .models import BlogPost, Comment, Like, Donation

class DonationInline(admin.TabularInline):
    model = Donation
    extra = 0
    readonly_fields = ('donor', 'amount', 'transaction_id', 'status', 'created_at')
    can_delete = False

class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'allow_donation', 'total_donations', 'created_at', 'likes_count')
    list_filter = ('category', 'allow_donation', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'author')
    inlines = [DonationInline]

    def save_model(self, request, obj, form, change):
        if not change: # Only set author on creation
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def total_donations(self, obj):
        return obj.total_donations
    total_donations.short_description = 'Total Donations'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'post__title')

class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'post', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    readonly_fields = ('donor', 'post', 'amount', 'transaction_id', 'created_at')

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like)
admin.site.register(Donation, DonationAdmin)

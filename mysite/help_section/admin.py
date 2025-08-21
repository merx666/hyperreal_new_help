from django.contrib import admin
from .models import Facility, Comment, RatingCategory, FacilityRating, Notification, NotificationPreference, Newsletter

@admin.action(description='Zatwierdź wybrane komentarze')
def approve_comments(modeladmin, request, queryset):
    queryset.update(is_approved=True)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'facility', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'facility__name')
    actions = [approve_comments]

class RatingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'email', 'notification_type', 'priority', 'is_read', 'is_sent', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_sent', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'email')
    readonly_fields = ('created_at', 'sent_at')
    ordering = ('-created_at',)

class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_notifications', 'new_facilities', 'facility_updates', 'new_comments', 'new_ratings', 'newsletter')
    list_filter = ('email_notifications', 'new_facilities', 'facility_updates', 'new_comments', 'new_ratings', 'newsletter')
    search_fields = ('user__username',)

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
    ordering = ('-created_at',)

# Rejestracja modeli w panelu admina
admin.site.register(Facility)
admin.site.register(Comment, CommentAdmin)
admin.site.register(RatingCategory, RatingCategoryAdmin)
admin.site.register(FacilityRating)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationPreference, NotificationPreferenceAdmin)
admin.site.register(Newsletter, NewsletterAdmin)

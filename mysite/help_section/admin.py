from django.contrib import admin
from .models import Facility, Comment, RatingCategory, FacilityRating

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

# Rejestracja modeli w panelu admina
admin.site.register(Facility)
admin.site.register(Comment, CommentAdmin)
admin.site.register(RatingCategory, RatingCategoryAdmin)
admin.site.register(FacilityRating)

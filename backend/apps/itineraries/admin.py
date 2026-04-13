from django.contrib import admin

from .models import QuizResult, SavedItinerary


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'personality_type', 'created_at']
    list_filter = ['personality_type']
    search_fields = ['user__username']
    ordering = ['-created_at']


@admin.register(SavedItinerary)
class SavedItineraryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'destination', 'personality_type', 'trip_duration', 'created_at']
    list_filter = ['personality_type']
    search_fields = ['user__username', 'title', 'destination']
    ordering = ['-created_at']

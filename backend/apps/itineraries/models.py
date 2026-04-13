from django.contrib.auth.models import User
from django.db import models


class QuizResult(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_results',
    )
    personality_type = models.CharField(max_length=100)
    # Stores quiz answers as a JSON object.
    # Example: {"q1": "adventure", "q2": "mountains", "q3": "solo"}
    answers = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.personality_type} ({self.created_at.date()})'


class SavedItinerary(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='itineraries',
    )
    destination = models.CharField(max_length=200)
    title = models.CharField(max_length=300)
    personality_type = models.CharField(max_length=100)
    trip_duration = models.CharField(max_length=50)
    # Stores the full itinerary as JSON.
    # Example: [{"day": 1, "title": "Arrival", "activities": ["Check in", "Explore"]}]
    itinerary_details = models.JSONField()
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'saved itineraries'

    def __str__(self):
        return f'{self.user.username} — {self.title}'

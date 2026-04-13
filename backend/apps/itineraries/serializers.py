from rest_framework import serializers

from .models import QuizResult, SavedItinerary


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['id', 'personality_type', 'answers', 'created_at']
        read_only_fields = ['id', 'created_at']


class SavedItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedItinerary
        fields = [
            'id',
            'destination',
            'title',
            'personality_type',
            'trip_duration',
            'itinerary_details',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

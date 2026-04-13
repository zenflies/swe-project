from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import QuizResult, SavedItinerary
from .serializers import QuizResultSerializer, SavedItinerarySerializer


class QuizResultListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/quiz-results/ — list quiz results for the logged-in user.
    POST /api/quiz-results/ — save a new quiz result.

    POST body:
        {
            "personality_type": "The Explorer",
            "answers": {"q1": "adventure", "q2": "mountains"}
        }
    """

    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users only ever see their own results.
        return QuizResult.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Attach the logged-in user automatically — never trust the client.
        serializer.save(user=self.request.user)


class ItineraryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/itineraries/ — list saved itineraries for the logged-in user.
    POST /api/itineraries/ — save a new itinerary.

    POST body:
        {
            "destination": "Patagonia, Argentina",
            "title": "7 Days in Patagonia",
            "personality_type": "The Explorer",
            "trip_duration": "7 days",
            "itinerary_details": [
                {"day": 1, "title": "Arrival", "activities": ["Check in"]}
            ],
            "notes": "Pack warm layers!"
        }
    """

    serializer_class = SavedItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedItinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ItineraryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/itineraries/<id>/ — retrieve a single itinerary.
    PUT    /api/itineraries/<id>/ — fully update an itinerary.
    PATCH  /api/itineraries/<id>/ — partially update an itinerary.
    DELETE /api/itineraries/<id>/ — delete an itinerary.

    All methods return 404 if the itinerary doesn't belong to the current user.
    """

    serializer_class = SavedItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Scoped to the current user so no one can access others' data.
        return SavedItinerary.objects.filter(user=self.request.user)

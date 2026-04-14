from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import QuizResult, SavedItinerary
from .serializers import QuizResultSerializer, SavedItinerarySerializer

class QuizResultViewSet(viewsets.ModelViewSet):
    serializer_class = QuizResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return the quiz results belonging to the logged-in user
        return QuizResult.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Delete any old results so they only have one active personality profile at a time
        QuizResult.objects.filter(user=self.request.user).delete()
        serializer.save(user=self.request.user)

class SavedItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = SavedItinerarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedItinerary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
from django.urls import path

from .views import ItineraryDetailView, ItineraryListCreateView, QuizResultListCreateView

urlpatterns = [
    path('quiz-results/', QuizResultListCreateView.as_view(), name='quiz-results'),
    path('itineraries/', ItineraryListCreateView.as_view(), name='itineraries'),
    path('itineraries/<int:pk>/', ItineraryDetailView.as_view(), name='itinerary-detail'),
]

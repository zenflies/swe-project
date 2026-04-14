from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizResultViewSet, SavedItineraryViewSet

router = DefaultRouter()
router.register(r'quiz-results', QuizResultViewSet, basename='quiz-results')
router.register(r'itineraries', SavedItineraryViewSet, basename='itineraries')

urlpatterns = [
    path('', include(router.urls)),
]
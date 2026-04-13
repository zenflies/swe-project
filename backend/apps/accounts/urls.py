from django.urls import path

from .views import LoginView, LogoutView, MeView, SignupView, csrf_view

urlpatterns = [
    path('csrf/', csrf_view, name='csrf'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
]

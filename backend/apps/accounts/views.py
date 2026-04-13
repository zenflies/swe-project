from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignupSerializer, UserSerializer


@ensure_csrf_cookie
@require_GET
def csrf_view(request):
    """
    GET /api/csrf/

    Sets the csrftoken cookie so the frontend can read it and attach it
    as an X-CSRFToken header on subsequent write requests (POST/PUT/DELETE).

    Call this once when your app loads, before any authenticated actions.
    """
    return JsonResponse({'detail': 'CSRF cookie set.'})


class SignupView(APIView):
    """
    POST /api/signup/

    Register a new user. Logs the user in immediately after signup.

    Request body:
        { "username": "...", "email": "...", "password": "..." }

    Returns:
        201 — user data (id, username, email, date_joined)
        400 — validation errors
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/login/

    Authenticate with email + password. Creates a session on success.

    Request body:
        { "email": "...", "password": "..." }

    Returns:
        200 — user data
        400 — missing fields
        401 — invalid credentials
    """

    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.models import User as UserModel

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Look up the account by email, then authenticate by username.
        try:
            user_obj = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    """
    POST /api/logout/

    Destroy the current session. Requires the X-CSRFToken header.

    Returns:
        200 — success message
        403 — not authenticated or missing CSRF token
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'})


class MeView(APIView):
    """
    GET /api/me/

    Return the currently logged-in user's data.

    Returns:
        200 — user data
        403 — not authenticated
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

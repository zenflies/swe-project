import json
import requests
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class Auth0JWTAuthentication(BaseAuthentication):
    """
    Authenticates requests using an Auth0 JWT via the Authorization header.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        domain = getattr(settings, 'AUTH0_DOMAIN', '')
        audience = getattr(settings, 'AUTH0_AUDIENCE', '')

        if not domain or not audience:
            raise AuthenticationFailed('Auth0 is not configured on the server.')

        # Fetch JWKS (JSON Web Key Set) from Auth0
        jwks_url = f'https://{domain}/.well-known/jwks.json'
        try:
            jwks = requests.get(jwks_url).json()
        except Exception:
            raise AuthenticationFailed('Unable to fetch JWKS from Auth0.')

        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token header.')

        rsa_key = {}
        for key in jwks.get('keys', []):
            if key['kid'] == unverified_header.get('kid'):
                rsa_key = {k: key[k] for k in ['kty', 'kid', 'use', 'n', 'e']}
                break
        
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(rsa_key)),
                    algorithms=['RS256'],
                    audience=audience,
                    issuer=f'https://{domain}/'
                )
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token has expired.')
            except jwt.InvalidTokenError:
                raise AuthenticationFailed('Invalid token or claims.')

            # Create or fetch the user based on their Auth0 subject ID
            username = payload.get('sub')
            if not username:
                raise AuthenticationFailed('Token has no subject claim.')

            user, _ = User.objects.get_or_create(username=username[:150])
            return (user, token)
            
        raise AuthenticationFailed('Unable to find an appropriate key to verify token.')
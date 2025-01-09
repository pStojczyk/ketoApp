"""
This module implements the `ParamTokenAuthentication` class, which allows for token-based
authentication through a query parameter. The token is validated against the database, and if valid,
the associated user is returned for further processing in the request lifecycle.
Usage:
    To use the `ParamTokenAuthentication`, include it in the `DEFAULT_AUTHENTICATION_CLASSES`
    setting in your Django REST Framework configuration.
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


class ParamTokenAuthentication(BaseAuthentication):
    """
    Custom authentication class that uses a token provided as a query parameter.
    This authentication method retrieves the token from the query parameters
    of the request and validates it against the stored tokens in the database.
    If the token is valid, the associated user is returned. If the token is
    missing or invalid, an AuthenticationFailed exception is raised.

    Usage:
        To authenticate a request, include the token in the query parameters:
        ?token=<your_token>
    """
    def authenticate(self, request):
        """
        Authenticate the request using a token provided in the query parameters.
        Args:
            request: The HTTP request object.
        Returns:
            A tuple of (user, token) if authentication is successful,
            or None if no token is provided.
        Raises:
            AuthenticationFailed: If the token is invalid or does not exist.
        """
        token_key = request.query_params.get('token')
        if not token_key:
            return None

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            msg = 'Invalid token. Please provide a valid token to access this resource.'
            raise AuthenticationFailed(msg)

        return token.user, token


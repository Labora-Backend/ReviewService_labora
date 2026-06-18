from functools import wraps
import logging
import os

import jwt
from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.response import Response


# ==========================================
# SERVICE USER
# ==========================================

class ServiceUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.role = str(role).lower() if role else None
        self.is_authenticated = True


logger = logging.getLogger(__name__)


# ==========================================
# JWT AUTHENTICATION
# ==========================================

class CustomJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        print("CUSTOM JWT AUTH CALLED")

        auth_header = request.META.get(
            "HTTP_AUTHORIZATION",
            ""
        )

        print("AUTH HEADER:", auth_header)



        if not auth_header:
            print("NO AUTH HEADER")
            raise exceptions.AuthenticationFailed(
                "Missing Authorization header."
            )

        print("HEADER FOUND")

        if not auth_header.startswith("Bearer "):
            print("INVALID FORMAT")
            raise exceptions.AuthenticationFailed(
                "Invalid Authorization header format."
            )

        token = auth_header.split(" ", 1)[1].strip()

        print("TOKEN EXTRACTED")

        payload = self._decode_token(token)

        print("PAYLOAD:", payload)

        user = ServiceUser(
            user_id=payload["user_id"],
            role=payload["role"]
        )

        print("USER CREATED:", user.id, user.role)

        return (user, payload)

    def _decode_token(self, token):

        print("DECODING TOKEN")

        public_key = getattr(
            settings,
            "JWT_PUBLIC_KEY",
            None
        )

        if not public_key:
            raise exceptions.AuthenticationFailed(
                "JWT public key is not configured."
            )

        expected_issuer = os.getenv("JWT_ISSUER")
        expected_audience = os.getenv("JWT_AUDIENCE")

        try:

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                issuer=expected_issuer if expected_issuer else None,
                audience=expected_audience if expected_audience else None,
                options={
                    "verify_aud": bool(expected_audience)
                }
            )

            print("TOKEN DECODED:", payload)

            return payload

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                "Token has expired."
            )

        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(
                f"Invalid token: {str(e)}"
            )


# ==========================================
# ROLE DECORATOR
# ==========================================

def role_required(allowed_roles):

    allowed_roles = [
        role.lower()
        for role in allowed_roles
    ]

    def decorator(view_func):

        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            user = request.user

            if not user or not user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            role = getattr(user, "role", None)

            if role is None:
                return Response(
                    {"error": "User role not found"},
                    status=status.HTTP_403_FORBIDDEN
                )

            if role.lower() not in allowed_roles:
                return Response(
                    {
                        "error": "Permission denied",
                        "required_roles": allowed_roles,
                        "your_role": role
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator


# ==========================================
# READY TO USE DECORATORS
# ==========================================

def admin_only(view_func):
    return role_required(["admin"])(view_func)


def client_only(view_func):
    return role_required(["client"])(view_func)


def freelancer_only(view_func):
    return role_required(["freelancer"])(view_func)


def client_or_admin(view_func):
    return role_required(
        ["client", "admin"]
    )(view_func)


def freelancer_or_admin(view_func):
    return role_required(
        ["freelancer", "admin"]
    )(view_func)
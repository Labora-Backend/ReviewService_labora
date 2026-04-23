from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def role_required(allowed_roles):
    """
    allowed_roles = ["ADMIN", "CLIENT", "FREELANCER"]
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            user = request.user

            # 1️⃣ Check authentication
            if not user or not user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # 2️⃣ Check role attribute exists
            if not hasattr(user, "role"):
                return Response(
                    {"error": "User role not defined"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 3️⃣ Check permission
            if user.role not in allowed_roles:
                return Response(
                    {
                        "error": "Permission denied",
                        "required_roles": allowed_roles,
                        "your_role": user.role
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
def admin_only(view_func):
    return role_required(["ADMIN"])(view_func)


def client_only(view_func):
    return role_required(["CLIENT"])(view_func)


def freelancer_only(view_func):
    return role_required(["FREELANCER"])(view_func)


def client_or_admin(view_func):
    return role_required(["CLIENT", "ADMIN"])(view_func)


def freelancer_or_admin(view_func):
    return role_required(["FREELANCER", "ADMIN"])(view_func)
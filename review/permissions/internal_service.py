from rest_framework.permissions import BasePermission
from django.conf import settings
from secrets import compare_digest


class IsInternalService(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        service_key = request.headers.get(
            "X-Service-Key"
        )

        return compare_digest(
            str(service_key),
            str(settings.SERVICE_API_KEY)
        )
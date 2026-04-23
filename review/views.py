
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .authentication import client_only, admin_only
from .models import Application, Review
from rest_framework import status
from .serializers import ReviewSerializer
#
# @api_view(["POST"])
# def review_application(request):
#     application_id = request.data.get("application_id")
#     status_value = request.data.get("status")
#
#     try:
#         app = Application.objects.get(id=application_id)
#         app.status = status_value
#         app.save()
#         return Response({"message": "Application reviewed successfully"})
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found"}, status=404)
#
#


@api_view(["POST"])
@client_only
def create_review(request):
    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Review added successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@admin_only
def admin_reviews(request):
    reviews = Review.objects.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

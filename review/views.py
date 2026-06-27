
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Avg, Count
import requests
import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from labora_shared.notification_client import send_notification
from .authentication import CustomJWTAuthentication
from .permissions.internal_service import IsInternalService
from .models import Review
from .serializers import ReviewSerializer, InternalReviewListSerializer

logger = logging.getLogger(__name__)


def get_rating_stats(user_id):
    stats = (
        Review.objects
        .filter(reviewee_id=user_id)
        .aggregate(
            average_rating=Avg("rating"),
            total_reviews=Count("id")
        )
    )

    return {
        "average_rating": round(stats["average_rating"], 2)
        if stats["average_rating"] else 0,
        "total_reviews": stats["total_reviews"]
    }


class CreateReviewView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):

        user = request.user

        if user.role not in ["client", "freelancer"]:
            return Response(
                {
                    "error": "Only clients and freelancers can submit reviews"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        reviewee_id = serializer.validated_data["reviewee_id"]
        job_id = serializer.validated_data["job_id"]

        # Verify job
        try:
            job_response = requests.get(
                f"{settings.JOB_SERVICE_URL}/api/internal/jobs/{job_id}/",
                headers={
                    "X-Service-Key": settings.SERVICE_API_KEY
                },
                timeout=5
            )

        except requests.RequestException:
            return Response(
                {
                    "error": "Unable to verify job"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if job_response.status_code != 200:
            return Response(
                {
                    "error": "Job not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        job_data = job_response.json()

        client_id = job_data.get("client_id")
        freelancer_id = job_data.get("freelancer_id")
        job_status = job_data.get("status")

        # Job must be completed
        if job_status != "completed":
            return Response(
                {
                    "error": "Reviews are allowed only after job completion"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # User must belong to the job
        if user.id not in [client_id, freelancer_id]:
            return Response(
                {
                    "error": "You are not a participant in this job"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Determine expected reviewee
        expected_reviewee = (
            freelancer_id if user.id == client_id else client_id
        )

        if reviewee_id != expected_reviewee:
            return Response(
                {
                    "error": "Invalid reviewee for this job"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prevent self-review
        if reviewee_id == user.id:
            return Response(
                {
                    "error": "You cannot review yourself"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            with transaction.atomic():

                review = serializer.save(
                    reviewer_id=user.id
                )

                transaction.on_commit(
                    lambda: send_notification(
                        user_id=reviewee_id,
                        notification_type="review_received",
                        title="New Review",
                        message="You received a new review."
                    )
                )

        except IntegrityError:
            return Response(
                {
                    "error": "You already reviewed this user for this job"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sync rating after successful commit
        try:

            stats = get_rating_stats(reviewee_id)

            response = requests.patch(
                f"{settings.FREELANCER_PROFILE_SERVICE_URL}"
                f"/api/internal/freelancers/{reviewee_id}/rating/",
                json=stats,
                headers={
                    "X-Service-Key": settings.SERVICE_API_KEY
                },
                timeout=5
            )

            response.raise_for_status()

        except requests.RequestException as e:

            logger.error(
                "Failed to sync rating for user %s: %s",
                reviewee_id,
                str(e)
            )

        return Response(
            {
                "message": "Review submitted successfully",
                "data": ReviewSerializer(review).data
            },
            status=status.HTTP_201_CREATED
        )


class UserReviewsView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, user_id):

        reviews = (
            Review.objects
            .filter(reviewee_id=user_id)
            .order_by("-created_at")
        )

        serializer = ReviewSerializer(
            reviews,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ReviewDetailView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, review_id):

        try:

            review = Review.objects.get(
                id=review_id
            )

        except Review.DoesNotExist:

            return Response(
                {
                    "error": "Review not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReviewSerializer(review)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class UserRatingView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, user_id):

        return Response(
            {
                "user_id": user_id,
                **get_rating_stats(user_id)
            },
            status=status.HTTP_200_OK
        )


class InternalUserRatingView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request, user_id):

        return Response(
            get_rating_stats(user_id),
            status=status.HTTP_200_OK
        )


class InternalReviewListView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request):

        reviews = Review.objects.all().order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 20

        page = paginator.paginate_queryset(
            reviews,
            request
        )

        serializer = InternalReviewListSerializer(
            page,
            many=True
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class InternalReviewStatsView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request):

        return Response({

            "total_reviews": Review.objects.count(),

            "five_star_reviews": Review.objects.filter(
                rating=5
            ).count(),

            "four_star_reviews": Review.objects.filter(
                rating=4
            ).count(),

            "three_star_reviews": Review.objects.filter(
                rating=3
            ).count(),

            "two_star_reviews": Review.objects.filter(
                rating=2
            ).count(),

            "one_star_reviews": Review.objects.filter(
                rating=1
            ).count(),

        })


class InternalReviewDetailView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def get(self, request, review_id):

        try:

            review = Review.objects.get(
                pk=review_id
            )

        except Review.DoesNotExist:

            return Response(
                {
                    "error": "Review not found"
                },
                status=404
            )

        serializer = InternalReviewListSerializer(
            review
        )

        return Response(
            serializer.data
        )


class InternalDeleteReviewView(APIView):
    authentication_classes = []

    permission_classes = [IsInternalService]

    def delete(self, request, review_id):

        try:

            review = Review.objects.get(
                pk=review_id
            )

        except Review.DoesNotExist:

            return Response(
                {
                    "error": "Review not found"
                },
                status=404
            )

        review.delete()

        return Response(
            {
                "message": "Review deleted successfully"
            }
        )
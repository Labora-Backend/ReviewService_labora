from django.db.models import Avg
from django.conf import settings
import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .authentication import CustomJWTAuthentication
from .permissions.internal_service import IsInternalService
from .models import Review
from .serializers import ReviewSerializer
import logging

logger = logging.getLogger(__name__)
def get_rating_stats(user_id):

    reviews = Review.objects.filter(
        reviewee_id=user_id
    )

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    return {
        "average_rating": round(
            average_rating, 2
        ) if average_rating else 0,
        "total_reviews": reviews.count()
    }
class CreateReviewView(APIView):

    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        print(request.headers.get("Authorization"))
        user = request.user

        if user.role not in ["client", "freelancer"]:

            return Response(
                {
                    "error": "Only clients and freelancers can submit reviews"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ReviewSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        reviewee_id = serializer.validated_data.get(
            "reviewee_id"
        )

        job_id = serializer.validated_data.get(
            "job_id"
        )

        # -----------------------------
        # VERIFY JOB FROM JOB SERVICE
        # -----------------------------

        try:

            job_response = requests.get(
                f"{settings.JOB_SERVICE_URL}/api/internal/jobs/{job_id}/",
                headers={
                    "X-Service-Key": settings.SERVICE_API_KEY
                },
                timeout=5
            )
            print(job_response.status_code)
            print(job_response.text)
            print("JOB RESPONSE STATUS")
            print(job_response.status_code)

            print("JOB RESPONSE BODY")
            print(job_response.text)

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

        client_id = job_data.get(
            "client_id"
        )

        freelancer_id = job_data.get(
            "freelancer_id"
        )

        job_status = job_data.get(
            "status"
        )

        # -----------------------------
        # JOB MUST BE COMPLETED
        # -----------------------------

        if job_status != "completed":

            return Response(
                {
                    "error": "Reviews are allowed only after job completion"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # REVIEWER MUST BELONG TO JOB
        # -----------------------------

        if user.id not in [
            client_id,
            freelancer_id
        ]:

            return Response(
                {
                    "error": "You are not a participant in this job"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -----------------------------
        # VALID REVIEW TARGET
        # -----------------------------

        if user.id == client_id:
            expected_reviewee = freelancer_id
        else:
            expected_reviewee = client_id

        if reviewee_id != expected_reviewee:

            return Response(
                {
                    "error": "Invalid reviewee for this job"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # PREVENT SELF REVIEW
        # -----------------------------

        if reviewee_id == user.id:

            return Response(
                {
                    "error": "You cannot review yourself"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # PREVENT DUPLICATE REVIEW
        # -----------------------------

        if Review.objects.filter(
            reviewer_id=user.id,
            reviewee_id=reviewee_id,
            job_id=job_id
        ).exists():

            return Response(
                {
                    "error": "You already reviewed this user for this job"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # SAVE REVIEW
        # -----------------------------

        review = serializer.save(
            reviewer_id=user.id
        )

        # -----------------------------
        # UPDATE FREELANCER PROFILE
        # -----------------------------

        stats = get_rating_stats(
            reviewee_id
        )

        try:
            print("RATING STATS:", stats)
            print("SYNCING RATING")
            print("USER:", reviewee_id)
            print("STATS:", stats)
            response = requests.patch(
                f"{settings.FREELANCER_PROFILE_SERVICE_URL}/api/internal/freelancers/{reviewee_id}/rating/",
                json=stats,
                headers={
                    "X-Service-Key": settings.SERVICE_API_KEY
                },
                timeout=5
            )
            print("PATCH STATUS:", response.status_code)
            print("PATCH BODY:", response.text)

            response.raise_for_status()

        except requests.RequestException as e:

            logger.error(
                f"Failed to sync rating for user {reviewee_id}: {str(e)}"
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

        reviews = Review.objects.filter(
            reviewee_id=user_id
        ).order_by("-created_at")

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

            serializer = ReviewSerializer(
                review
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Review.DoesNotExist:

            return Response(
                {
                    "error": "Review not found"
                },
                status=status.HTTP_404_NOT_FOUND
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

    permission_classes = [IsInternalService]

    def get(self, request, user_id):

        return Response(
            get_rating_stats(user_id),
            status=status.HTTP_200_OK
        )
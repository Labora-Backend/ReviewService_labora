from django.urls import path
from .views import (
    CreateReviewView,
    UserReviewsView,
    ReviewDetailView,
    UserRatingView,
    InternalUserRatingView,
)

urlpatterns = [

    path(
        "reviews/create/",
        CreateReviewView.as_view()
    ),

    path(
        "reviews/user/<int:user_id>/",
        UserReviewsView.as_view()
    ),

    path(
        "reviews/<int:review_id>/",
        ReviewDetailView.as_view()
    ),

    path(
        "reviews/user/<int:user_id>/rating/",
        UserRatingView.as_view()
    ),

    path(
        "internal/users/<int:user_id>/rating/",
        InternalUserRatingView.as_view()
    ),
]
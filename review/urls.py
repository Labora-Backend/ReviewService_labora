from django.urls import path
from .views import (
    CreateReviewView,
    UserReviewsView,
    ReviewDetailView,
    UserRatingView,
    InternalUserRatingView, InternalReviewListView, InternalReviewStatsView, InternalReviewDetailView,
    InternalDeleteReviewView,
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
    path(
        "internal/reviews/",
        InternalReviewListView.as_view()
    ),

    path(
        "internal/reviews/stats/",
        InternalReviewStatsView.as_view()
    ),

    path(
        "internal/reviews/<int:review_id>/",
        InternalReviewDetailView.as_view()
    ),

    path(
        "internal/reviews/<int:review_id>/delete/",
        InternalDeleteReviewView.as_view()
    ),
]
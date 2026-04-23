
from django.urls import path
from review import views

urlpatterns = [
    # path("client/applications/review/",views.review_application),
    path("client/reviews/create/",views.create_review),
    path("admin/reviews/",views.admin_reviews),
]

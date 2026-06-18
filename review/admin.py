from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job_id",
        "reviewer_id",
        "reviewee_id",
        "rating",
        "created_at",
    )
    list_filter = ("rating", "created_at")
    search_fields = ("job_id", "reviewer_id", "reviewee_id", "comment")
    readonly_fields = ("created_at",)


from django.db import models

class Review(models.Model):

    reviewer_id = models.BigIntegerField()

    reviewee_id = models.BigIntegerField()

    job_id = models.BigIntegerField()

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "reviewer_id",
                    "reviewee_id",
                    "job_id"
                ],
                name="unique_review_per_job"
            )
        ]
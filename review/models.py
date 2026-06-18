
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
        db_table = "reviews"
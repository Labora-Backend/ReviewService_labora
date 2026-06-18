from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review

        fields = [
            "id",
            "job_id",
            "reviewer_id",
            "reviewee_id",
            "rating",
            "comment",
            "created_at"
        ]

        read_only_fields = [
            "id",
            "reviewer_id",
            "created_at"
        ]

    def validate_comment(self, value):

        if value and len(value) > 2000:

            raise serializers.ValidationError(
                "Comment must be 2000 characters or fewer."
            )

        return value
# Labora Review Service

Production-ready Django REST Framework microservice for review and rating workflows.

## Responsibilities

- Create one review per reviewer per completed job.
- Verify job status and participants through the Job Service API.
- Prevent self-reviews, fake reviews, and duplicates.
- Expose user and job review lists with average rating and total review counts.
- Support reviewer-only updates, reviewer/admin soft deletes, admin review listing, pagination, and sorting.
- Verify Auth Service JWT access tokens with the RS256 public key.
- Publish `review_posted` events to the Notification Service.

## API

Swagger UI is available at:

```text
GET /api/docs/
```

Core endpoints:

```text
POST   /reviews/
GET    /reviews/                       # admin only
PUT    /reviews/{id}/                  # original reviewer only, 24h default edit window
DELETE /reviews/{id}/                  # original reviewer or admin
GET    /reviews/user/{user_id}/
GET    /reviews/job/{job_id}/
```

The same routes are also mounted below `/api/` for gateway compatibility.

## Example Requests

Create a review:

```bash
curl -X POST http://localhost:8009/reviews/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 42,
    "reviewee_id": 19,
    "rating": 5,
    "comment": "Clear scope, fast feedback, and smooth delivery."
  }'
```

Get reviews for a user:

```bash
curl "http://localhost:8009/reviews/user/19/?sort=highest_rating&page=1&page_size=20" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Delete a review:

```bash
curl -X DELETE http://localhost:8009/reviews/7/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Environment

Copy `.env.template` to `.env` and configure:

```text
JWT_PUBLIC_KEY_PATH=/app/jwt_keys/public.pem
JOB_DETAIL_URL_TEMPLATE=http://job-service:8000/api/jobs/{job_id}/
NOTIFICATION_EVENT_URL=http://notification-service:8000/api/notifications/create/
REVIEW_EDIT_WINDOW_HOURS=24
```

This service stores external identifiers as integers only. It does not create direct foreign keys to user, job, payment, or application tables.

## Local Development

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8009
```

## Docker

From the repository root:

```bash
docker-compose up --build review_service
```

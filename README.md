# Review Service

Review Service stores job reviews and rating statistics for Labora. It verifies job participation and completion through Job Service before accepting a review, notifies the reviewee, and synchronizes freelancer rating totals.

## Responsibilities

- Let clients and freelancers review each other after a completed job.
- Return reviews and rating statistics for a user.
- Prevent duplicate reviews for the same reviewer/reviewee/job combination.
- Provide internal review list, detail, delete, and statistics endpoints for Admin Service.
- Synchronize freelancer rating totals with Freelancer Profile Service.

## Features

- Completed-job validation through Job Service.
- Participant validation against job `client_id` and resolved `freelancer_id`.
- Self-review prevention.
- Comment length validation capped at 2000 characters.
- Rating aggregation using average rating and total review count.

## API Endpoints

Base path: `/api/`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `reviews/create/` | Client or freelancer JWT | Create a review after job completion. |
| `GET` | `reviews/user/<user_id>/` | Bearer JWT | List reviews received by a user. |
| `GET` | `reviews/<review_id>/` | Bearer JWT | Return one review. |
| `GET` | `reviews/user/<user_id>/rating/` | Bearer JWT | Return average rating and review count for a user. |

## Internal Service Endpoints

Internal endpoints use `X-Service-Key: <SERVICE_API_KEY>`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `internal/users/<user_id>/rating/` | Return aggregate rating stats. |
| `GET` | `internal/reviews/` | Return paginated review summaries. |
| `GET` | `internal/reviews/stats/` | Return counts by star rating. |
| `GET` | `internal/reviews/<review_id>/` | Return one review summary. |
| `DELETE` | `internal/reviews/<review_id>/delete/` | Delete a review. |

## Authentication

User endpoints use `review.authentication.CustomJWTAuthentication`. Internal endpoints bypass JWT and require `X-Service-Key`.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django secret key. |
| `DEBUG` | Enables debug mode when set to `1`, `true`, or `yes`. |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts. Defaults to `*`. |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | MySQL database configuration. |
| `JWT_PUBLIC_KEY_PATH` | Public key used to verify Auth Service JWTs. |
| `SERVICE_API_KEY` | Shared key for internal calls. |
| `JOB_SERVICE_URL` | Used to verify job status and participants. |
| `FREELANCER_PROFILE_SERVICE_URL` | Used to synchronize rating totals. |
| `NOTIFICATION_SERVICE_URL` | Used by shared notification client. |
| `*_SERVICE_URL` | Additional service URL settings loaded by settings. |

## Setup

```bash
cd ReviewService_labora
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8009
```

## Service Architecture

- Django project: `ReviewService`
- App: `review`
- Authentication: `review.authentication.CustomJWTAuthentication`
- Internal permission: `review.permissions.internal_service.IsInternalService`
- Outbound dependencies: Job Service, Freelancer Profile Service, and Notification Service

## Database Models

- `Review`: stores reviewer id, reviewee id, job id, rating, comment, and timestamps. A unique constraint prevents duplicate reviews per reviewer/reviewee/job.

## Notification/Event Flow

After a review is committed, the service sends `review_received` to the reviewee. It then attempts to patch Freelancer Profile Service with updated rating stats; sync failure is logged and does not roll back the review.

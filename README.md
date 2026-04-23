# Review Service

This is a Django-based review service built as part of my microservice backend project.

This service is responsible for handling user reviews and related operations.

---

## What this service does

* Create and manage reviews
* Handle API requests related to reviews
* Works as an independent service in a microservice architecture

---

## Tech Used

* Python
* Django
* Django REST Framework
* Docker

---

## Project Structure

```text
ReviewService/
│
├── review/                # App logic (models, views, serializers)
├── ReviewService/         # Main Django project
├── jwt_keys/              # JWT keys (ignored in git)
├── manage.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## How to Run

### 1. Clone the repo

```bash
git clone https://github.com/YOUR-USERNAME/ReviewService.git
cd ReviewService
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start server

```bash
python manage.py runserver
```

---

## Run with Docker

```bash
docker build -t review-service .
docker run -p 8000:8000 review-service
```

---

## Notes

* `.env`, `jwt_keys/`, and `.pem` files are ignored for security
* This service is part of a larger backend system

---


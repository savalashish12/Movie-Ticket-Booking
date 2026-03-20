# Movie-Ticket-Booking
I have done this backend application using Movie Ticket Booking Fast-API System.

🎬 CineStar Movie Booking API

This is a FastAPI-based Movie Ticket Booking System built as part of an academic project.
It allows users to browse movies, book tickets, hold seats, and manage bookings using REST APIs.

🚀 Features

View all movies with available seats

Get movie details by ID

Book tickets with pricing logic (premium, recliner, promo codes)

Add, update, and delete movies

Seat hold & confirmation workflow

Search, filter, sort, and paginate movies

Browse endpoint (combined filtering + sorting + pagination)

Booking management (search, sort, pagination)

🛠 Tech Stack

Backend: FastAPI

Language: Python

Validation: Pydantic

API Testing: Swagger UI (built-in)

▶️ How to Run

Install dependencies:

pip install fastapi uvicorn

Run the server:

uvicorn main:app --reload

Open in browser:

http://127.0.0.1:8000/docs
📌 API Overview
🎥 Movies

GET /movies → Get all movies

GET /movies/{id} → Get movie by ID

POST /movies → Add new movie

PUT /movies/{id} → Update movie

DELETE /movies/{id} → Delete movie

🎟 Bookings

POST /bookings → Book ticket

GET /bookings → View bookings

GET /bookings/search → Search bookings

GET /bookings/sort → Sort bookings

GET /bookings/page → Paginate bookings

🪑 Seat Workflow

POST /seat-hold → Hold seats

GET /seat-hold → View holds

POST /seat-confirm/{id} → Confirm hold

DELETE /seat-release/{id} → Release hold

🔍 Advanced Features

GET /movies/filter → Filter movies

GET /movies/search → Search movies

GET /movies/sort → Sort movies

GET /movies/page → Pagination

GET /movies/browse → Combined (filter + sort + page)

💡 Business Logic

Seat availability reduces after booking or hold

Promo codes:

SAVE10 → 10% discount

SAVE20 → 20% discount

Seat types:

Standard → Normal price

Premium → 1.5x

Recliner → 2x

Movies with active bookings cannot be deleted

🧪 Testing

All endpoints were tested using Swagger UI:

Valid and invalid inputs checked

Error handling (404, 400, 422) verified

Workflow (hold → confirm → release) tested
# AI Shopping Project – World Cup Jersey Store

## Overview

AI Shopping Project is a full-stack eCommerce web application built with:

* FastAPI (Python backend)
* Streamlit (frontend)
* MySQL
* Redis caching
* OpenAI Assistant integration

The application simulates an online World Cup jersey store where users can:

* Browse jerseys
* Filter/search products
* Add products to favorites
* Create and manage orders
* Purchase orders
* Chat with an AI shopping assistant

The project follows MVC architecture and includes authentication, caching, session management, and order handling logic.

---

# Setup & Run Instructions

## 1. Clone Repository

```bash
git clone <repository_url>
cd ai-shopping-project
```

---

# 2. Create Virtual Environment

```bash
python -m venv .venv
```

---

# 3. Activate Virtual Environment

## Windows

```bash
.venv\Scripts\activate
```

## Mac/Linux

```bash
source .venv/bin/activate
```

---

# 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 5. Create `.env` File

Create a `.env` file inside the `backend` folder:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini
```

---

# 6. Run Docker Containers

The project uses Docker for:

* MySQL database
* Redis cache

The database tables and initial jersey data are created automatically when the MySQL container starts.

Run:

```bash
cd backend
docker compose up -d
```

---

# 7. Run Backend

Open a new terminal:

```bash
cd backend
uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 8. Run Frontend

Open another terminal:

```bash
cd frontend
streamlit run app.py
```

Frontend URL:

```text
http://localhost:8501
```

---

# Project Features

## User System

* User registration
* User login/logout
* JWT authentication
* Delete account
* Username uniqueness validation

Each user contains:

* First name
* Last name
* Email
* Phone
* Country
* City
* Username
* Password (hashed)

---

# Products System

The store contains national football team jerseys for World Cup 2026.

Each product contains:

* Jersey name
* Price
* Stock quantity

Features:

* Product grid UI
* Country flag banners
* Search by jersey name
* Price filtering
* Stock filtering
* Sorting
* Out-of-stock handling

---

# Favorites System

Authenticated users can:

* Add jerseys to favorites
* Remove jerseys from favorites
* View favorite jerseys page

The favorites page displays:

* Flag image
* Jersey name
* Price
* Stock

---

# Orders System

Users can manage shopping orders.

## TEMP Orders

* Active pending cart
* Editable
* Persistent after logout
* Only one TEMP order per user

Users can:

* Add items
* Remove items
* Update quantities
* Purchase order

## CLOSE Orders

* Historical purchased orders
* Read-only
* Display full order details

Purchase flow:

* Validates stock
* Updates inventory
* Closes order

---

# AI Shopping Assistant

The system includes an OpenAI-powered assistant.

The assistant can:

* Recommend jerseys
* Explain stock availability
* Help users navigate the website
* Answer product-related questions

Additional features:

* Context-aware product information
* Website usage guidance
* Prompt usage limitation per session

---

# Caching

## Redis Cache (Backend)

Redis is used for backend caching of products.

Cached endpoint:

* `GET /item/`

Benefits:

* Faster response times
* Reduced database queries

---

## Streamlit Cache (Frontend)

The frontend uses:

```python
@st.cache_data(ttl=30)
```

to cache public product data for 30 seconds.

Benefits:

* Reduced API calls
* Improved frontend performance

---

# Technologies

## Backend

* Python
* FastAPI
* MySQL
* Redis
* OpenAI API
* JWT Authentication

## Frontend

* Streamlit
* Requests
* Pandas

## Other

* Docker
* Redis Insight
* HeidiSQL

---

# Architecture

The backend follows MVC architecture.

## Controller Layer

Handles API routes and HTTP requests.

## Service Layer

Contains business logic.

## Repository Layer

Handles database operations.

## Model Layer

Defines entities and request/response schemas.

---

# Database Tables

* users
* items
* favorite_items
* orders
* order_items

---

# Project Highlights

* Full-stack architecture
* JWT authentication
* Redis caching
* Streamlit caching
* OpenAI integration
* Persistent shopping cart
* Order management system
* Responsive grid UI
* Flag-based product design
* MVC architecture

---

# Screenshots

## Main Page

![Main Page](screenshots/main-page.png)

---

## Favorites Page

![Favorites Page](screenshots/favorites-page.png)

---

## Orders Page

![Orders Page](screenshots/orders-page.png)

---

## Chat Assistant

![Chat Assistant](screenshots/chat-page.png)

---

# Author

Alon Vizniuk
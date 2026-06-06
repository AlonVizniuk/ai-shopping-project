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

# Main Technologies

- FastAPI
- Streamlit
- MySQL
- Redis
- OpenAI API
- Scikit-learn
- Docker
- JWT Authentication

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

All frontend and backend dependencies are managed through the backend requirements.txt file.

```bash
cd backend
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

The frontend uses Streamlit's `@st.cache_data(ttl=30)` decorator
to cache public product data for 30 seconds.

Benefits:

* Reduced API calls
* Improved frontend performance

Additionally, the frontend uses Streamlit's `@st.cache_resource`
decorator to cache and reuse a shared HTTP session object across pages.

The cached session is used for communication with the FastAPI backend.

Benefits:

* Reduced repeated session creation
* Improved frontend resource management
* Shared reusable HTTP client across the application

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
* Jupyter Notebook
* Scikit-learn

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

# API Endpoints

## Authentication

- `POST /auth/token`

## Products

- `GET /item/`

## Favorites

- `GET /favorite/`
- `POST /favorite/{item_id}`
- `DELETE /favorite/{item_id}`

## Orders

- `GET /order/`
- `POST /order/add-item`
- `PUT /order/update-quantity`
- `DELETE /order/remove-item/{item_id}`
- `POST /order/purchase`

## AI Assistant

- `POST /chat/`

## Machine Learning

`GET /prediction/future-spending`

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
* Machine learning prediction integration
* Lasso Regression spending prediction model
* End-to-end ML workflow

---

# Machine Learning Bonus

A supervised machine learning model was integrated into the project in order to predict future user spending behavior.
The prediction system is fully integrated into both the FastAPI backend and the Streamlit frontend.

## Model Details
- Problem Type: Regression
- Model: Lasso Regression
- Hyperparameter Tuning: GridSearchCV
- Feature Scaling: StandardScaler

## Features Used
- Favorite items count
- Closed orders count
- Total purchased items
- Average order value
- Days since registration

## ML Workflow
1. Synthetic dataset generation
2. Data preprocessing and analysis
3. Correlation analysis
4. Model training and tuning
5. Model export using joblib
6. Backend inference integration
7. Frontend prediction visualization

## ML API Endpoint

`GET /prediction/future-spending`

## ML Files
backend/ml/

## Running the ML Training Notebook

The ML training process is documented inside the following Jupyter Notebook:

```text
backend/ml/user_spending_prediction.ipynb
```

The notebook includes:

- Dataset loading
- Data preprocessing
- Missing values analysis
- Duplicate rows analysis
- Exploratory data analysis
- Correlation analysis
- Train/test split
- Feature scaling using StandardScaler
- Lasso Regression training
- Hyperparameter tuning using GridSearchCV
- Model evaluation
- Model export using joblib
- Example prediction

To retrain the machine learning model, open the notebook and run all cells from top to bottom.

---

## Dataset Generation

The synthetic dataset is generated using:

```text
backend/ml/generate_dataset.py
```

The generated dataset file:

```text
backend/ml/user_spending_dataset.csv
```

Each row in the dataset represents a simulated user shopping behavior profile.

The dataset generation logic follows realistic shopping assumptions:

- Users with more favorite items are more likely to spend more in the future
- Users with more completed orders usually have higher future spending
- Users who purchased more items are expected to continue spending more
- Higher average order values increase future spending estimation
- Users registered for longer periods may have slightly higher spending potential

To regenerate the dataset:

```bash
cd backend
python ml/generate_dataset.py
```

After regenerating the dataset, rerun the notebook:

```text
backend/ml/user_spending_prediction.ipynb
```

The notebook will retrain the model and export updated model files:

```text
backend/ml/user_spending_lasso_model.pkl
backend/ml/user_spending_scaler.pkl
```

The FastAPI prediction endpoint automatically uses these exported files for inference.

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

## Future Spending Prediction

![Prediction Page](screenshots/prediction-page.png)


---

# Author

Alon Vizniuk
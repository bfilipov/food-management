# Food management

Born from a simple goal: stop throwing away forgotten groceries. 
This app tracks expiration dates and suggests practical meals to keep your kitchen fresh and waste-free.   

## Features
📦 Inventory Tracking – Add foods with names, quantities, and expiration dates  
⚠️ Smart Expiration Alerts – Visual indicators for items expiring soon or today  
🤖 AI Meal Recommendations – Daily recipe suggestions optimized for your current stock  
♻️ Waste Reduction Tips – Actionable advice to use partial quantities or preserve items  
🔄 Background Auto-Refresh – AI jobs trigger automatically when inventory changes  
🗄️ Persistent Recommendations – Latest AI output saved to PostgreSQL for instant loading  
📱 Simple Frontend – Clean, responsive UI with no external frameworks  

## Prerequisites
Docker & Docker Compose v2+  
Python 3.12+ (for local development)  
Poetry: `pip install poetry`  

### Option 1: Docker Compose (Recommended)  

```
# Clone the repository
git clone https://github.com/yourusername/food-management.git
cd food-management

# Configure environment variables
cp .env.example .env
# Edit .env with your AI endpoint and database credentials

# Build and start all services
docker compose up --build -d

# View application logs
docker compose logs -f app

# Open in your browser
open http://localhost:8000
```

### Option 2: Local Development  
```
# Install dependencies
poetry install

# Start PostgreSQL
docker run -d --name food-postgres \
  -e POSTGRES_DB=fooddb -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 postgres:16

# Set environment variables
export DATABASE_URL="postgresql+psycopg2://postgres:yourpassword@localhost:5432/fooddb"
export AI_ENDPOINT="http://localhost:8081/v1/chat"

# Run the app
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## ⚙️ Environment Configuration  

```
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=fooddb
POSTGRES_HOST=db
POSTGRES_PORT=5432

# AI Service (clone and run git@github.com:bfilipov/llm-proxy-api.git)
AI_ENDPOINT=http://localhost:8081/v1/chat

# App Settings
APP_HOST=0.0.0.0
APP_PORT=8000
```
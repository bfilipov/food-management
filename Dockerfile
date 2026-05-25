FROM python:3.12-slim

WORKDIR /app

# 1. Install Poetry
RUN pip install --no-cache-dir poetry

# 2. Copy dependency files FIRST (Docker layer caching)
COPY pyproject.toml poetry.lock ./

# 3. Disable Poetry venv creation & install only production deps
RUN poetry install --no-interaction --no-ansi --no-root

# 4. Copy application code
COPY . .

EXPOSE 8000

# Default command (overridden in docker-compose for dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
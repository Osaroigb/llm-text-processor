FROM python:3.12-alpine3.20

# System dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev build-base postgresql-dev libmagic

# Install Poetry using pip
RUN pip install poetry

WORKDIR /app

# Copy Poetry files first
COPY poetry.lock pyproject.toml ./

# Install dependencies without virtualenv
RUN poetry config virtualenvs.create false \
    && poetry install --no-root 

# Copy the app
COPY . .

# Expose port
EXPOSE 8000

# Default command for dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

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

# Download NLTK data during build in a non-interactive way
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True); nltk.download('perluniprops', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('averaged_perceptron_tagger_eng', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"

# Expose port
EXPOSE 8000

# Default command for dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

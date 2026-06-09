# TPW Lifecycle Platform — Cloud Run
# Supports both Streamlit dashboard and FastAPI via environment variable

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source
COPY config/ config/
COPY src/ src/
COPY jobs/ jobs/

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Default: run FastAPI API
# Override with: docker run -e APP_MODE=dashboard ...
ENV APP_MODE=api
ENV PORT=8080

EXPOSE 8080

CMD if [ "$APP_MODE" = "dashboard" ]; then \
        streamlit run src/dashboard/app.py \
            --server.port=$PORT \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --server.enableCORS=false; \
    else \
        uvicorn src.api.main:app \
            --host 0.0.0.0 \
            --port $PORT; \
    fi

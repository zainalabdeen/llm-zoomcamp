# -----------------------------
# 1. Base image with Python
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# 2. Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 3. Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 4. Install Python dependencies
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 5. Copy all source code
# -----------------------------
COPY . .

# -----------------------------
# 6. Set environment variables
# -----------------------------
# ⚠️ IMPORTANT: You should override these with real secrets in cloud deployment
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRSFPROTECTION=false

# Optional: PostgreSQL connection string (override in Render/Fly.io)
ENV POSTGRES_URL="postgresql://user:password@host:5432/dbname"
ENV QDRANT_URL="http://qdrant:6333"
ENV OPENAI_API_KEY="your-openai-key"
ENV ADMIN_PASSWORD="admin123"

# -----------------------------
# 7. Expose Streamlit port
# -----------------------------
EXPOSE 8501

# -----------------------------
# 8. Start both apps (user app + dashboard)
# -----------------------------
# main.py runs both on ports 8501 (app) and 8502 (dashboard)
CMD ["python", "main.py"]

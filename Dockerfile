# Use a lightweight official Python image
FROM python:3.11-slim
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

# Set working directory
WORKDIR /app

# Install system dependencies (for PDFs, OCR, psycopg2, and OpenCV)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the application files
COPY backend/ ./backend/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8080

# Pre-download Unstructured layout model (prevents runtime rate limits)

RUN python3 -c "from huggingface_hub import snapshot_download; snapshot_download('unstructuredio/yolo_x_layout', token='$HF_TOKEN')"


# Command to start the app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]

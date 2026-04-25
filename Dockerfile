FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Expose Gradio port (FastAPI runs on 8000 internally)
EXPOSE 7860

# Run the main entry point which starts both FastAPI and Gradio
CMD ["python", "main.py"]

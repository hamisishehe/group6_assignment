FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Use a production-grade WSGI server instead of `python app.py`
# If you want to use Flask's built-in server for dev only, keep CMD as is
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

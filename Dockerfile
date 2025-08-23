# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application code
COPY app.py /app

# Install Flask
RUN pip install flask

# Expose the port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]


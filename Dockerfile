# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Flask runs on 5000)
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
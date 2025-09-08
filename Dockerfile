FROM python:3.11-slim

# System dependencies 
RUN apt-get update && apt-get install -y \
    libjpeg-dev zlib1g-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 8000

# Run migrations + launch server
#CMD ["sh", "-c", "python manage.py migrate && gunicorn djbackend.wsgi:application --bind 0.0.0.0:8000"]

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn djbackend.wsgi:application --bind 0.0.0.0:8000"]


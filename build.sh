
#!/usr/bin/env bash
set -o errexit

# Install dependencies
apt-get update && apt-get install -y libjpeg-dev zlib1g-dev

pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Load fixtures (to maintain data!)
python manage.py loaddata initial_data.json || true

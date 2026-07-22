#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Creating logs directory..."
mkdir -p logs

echo "Creating cache directory..."
mkdir -p cache/search

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build complete!"
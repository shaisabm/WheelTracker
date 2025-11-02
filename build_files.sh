#!/bin/bash

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully!"

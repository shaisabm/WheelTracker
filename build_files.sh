#!/bin/bash

echo "Installing ODBC drivers and dependencies..."

# Install unixODBC
apt-get update
apt-get install -y unixodbc unixodbc-dev

# Install Microsoft ODBC Driver 18 for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18

echo "ODBC drivers installed successfully"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Build completed successfully!"

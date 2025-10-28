#!/bin/bash

# Startup script for Wheel Strategy Tracker development environment

echo "Starting Wheel Strategy Tracker..."
echo ""

# Check if Django server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Django server is already running on port 8000"
else
    echo "Starting Django backend server..."
    python manage.py runserver &
    DJANGO_PID=$!
    echo "Django server started with PID $DJANGO_PID"
fi

echo ""

# Check if frontend server is already running
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "Frontend server is already running on port 5173"
else
    echo "Starting Svelte frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend server started with PID $FRONTEND_PID"
fi

echo ""
echo "=========================================="
echo "Wheel Strategy Tracker is running!"
echo "=========================================="
echo "Backend API: http://localhost:8000/api/"
echo "Frontend:    http://localhost:5173/"
echo "Admin:       http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Wait for Ctrl+C
wait

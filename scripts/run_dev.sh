#!/bin/bash
# Development server script

# Set environment variables
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run the development server with auto-reload
echo "Starting development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 
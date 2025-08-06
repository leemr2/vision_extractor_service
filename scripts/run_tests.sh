#!/bin/bash
# Test runner script

# Set environment variables for testing
export API_KEY=test_api_key
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run pytest with coverage report
echo "Running tests with coverage..."
pytest --cov=app tests/ --cov-report=term-missing 
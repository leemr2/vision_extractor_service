#!/bin/bash
# Docker build script

# Set version
VERSION=${1:-latest}

# Build Docker image
echo "Building Docker image: vision-extractor-service:$VERSION"
docker build -t vision-extractor-service:$VERSION .

# Optionally tag for registry
if [ -n "$2" ]; then
    REGISTRY=$2
    echo "Tagging for registry: $REGISTRY/vision-extractor-service:$VERSION"
    docker tag vision-extractor-service:$VERSION $REGISTRY/vision-extractor-service:$VERSION
    
    # Push if specified
    if [ "$3" = "--push" ]; then
        echo "Pushing to registry: $REGISTRY/vision-extractor-service:$VERSION"
        docker push $REGISTRY/vision-extractor-service:$VERSION
    fi
fi

echo "Build complete!" 
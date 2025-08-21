#!/bin/bash
# Tajir POS Secure Deployment Script

echo "Deploying Tajir POS with security features..."

# Install security packages
pip install Flask-WTF==1.1.1 Flask-Limiter==3.5.0 marshmallow==3.20.1 cryptography==41.0.7

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Deploy to Railway
echo "Deploying to Railway..."
railway up

echo "Deployment completed!"
echo "Check your application at: railway open"

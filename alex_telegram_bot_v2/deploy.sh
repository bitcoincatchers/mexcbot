#!/bin/bash

echo "🚀 Deploying Alex's Telegram Bot v2.0..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set permissions
chmod +x main.py

echo "✅ Deployment complete!"
echo "Start bot: python main.py"

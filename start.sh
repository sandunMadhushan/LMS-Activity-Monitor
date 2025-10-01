#!/bin/bash

echo "=================================="
echo "LMS Activity Monitor - Quick Start"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your credentials."
    echo ""
    echo "Edit .env now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        ${EDITOR:-nano} .env
    else
        echo "Please edit .env before continuing."
        exit 0
    fi
fi

echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "What would you like to do?"
echo "1) Run a test scan (with browser visible)"
echo "2) Run a headless scan"
echo "3) Send test email"
echo "4) Start web dashboard"
echo "5) Exit"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "Running test scan with visible browser..."
        python scraper.py --headless False
        ;;
    2)
        echo "Running headless scan..."
        python scraper.py
        ;;
    3)
        echo "Sending test email..."
        python scraper.py --test-email
        ;;
    4)
        echo "Starting web dashboard..."
        echo "Open http://localhost:5000 in your browser"
        python app.py
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

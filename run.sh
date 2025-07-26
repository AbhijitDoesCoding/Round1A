#!/bin/bash

# PDF Challenge Runner Script
echo "🚀 PDF Challenge - Outline Extractor"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Function to run setup
setup() {
    echo "🔧 Setting up environment..."
    python3 setup.py
}

# Function to run Round 1A
round1a() {
    echo "📄 Running PDF Outline Extraction"
    python3 run_round1a.py "$@"
}

# Main menu
case "$1" in
    "setup")
        setup
        ;;
    "run")
        shift
        round1a "$@"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  setup    Set up the environment and install dependencies"
        echo "  run      Run the PDF Outline Extraction"
        echo "  help     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 setup"
        echo "  $0 run"
        echo "  $0 run input/ output/"
        ;;
    *)
        echo "❓ Unknown command: $1"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac
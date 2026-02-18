#!/bin/bash

# E-commerce Price Tracker - Project Setup Script

echo "=========================================="
echo "Mobility Delay Platform - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python packages..."
pip install -r requirements.txt

# Project build
echo ""
echo "Building project..."
pip install -e .

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
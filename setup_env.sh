#!/bin/bash
echo "Setting up Android Root Suite development environment..."
echo

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found! Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Ask about development tools
read -p "Install development tools? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing development tools..."
    pip install -r requirements-dev.txt
    pre-commit install
fi

echo
echo "Setup complete!"
echo
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo
echo "To run the application:"
echo "  python main.py"

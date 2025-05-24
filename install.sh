#!/bin/bash

# Hospital Outcomes Analyzer Installer for macOS

echo "Hospital Outcomes Analyzer Installer"
echo "===================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 found"

# Check Python version (need 3.8+)
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version $python_version is compatible"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv hospital_analyzer_env

# Activate virtual environment
source hospital_analyzer_env/bin/activate

echo "✓ Virtual environment created"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Make the script executable
chmod +x hospital_analyzer.py

# Create desktop launcher
cat > "Hospital Analyzer.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source hospital_analyzer_env/bin/activate
python3 hospital_analyzer.py
EOF

chmod +x "Hospital Analyzer.command"

echo "✓ Desktop launcher created"

echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the Hospital Outcomes Analyzer:"
echo "1. Double-click 'Hospital Analyzer.command' in this folder"
echo "2. Or run: ./hospital_analyzer.py"
echo ""
echo "The application will load the included Excel data automatically."
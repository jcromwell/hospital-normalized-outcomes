#!/bin/bash

# Hospital Outcomes Analyzer Web App Installer for macOS

echo "Hospital Outcomes Analyzer Web App Installer"
echo "============================================="

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
python3 -m venv hospital_web_env

# Activate virtual environment
source hospital_web_env/bin/activate

echo "✓ Virtual environment created"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing web app dependencies..."
pip install -r requirements_web.txt

echo "✓ Dependencies installed"

# Create launch script
cat > "Hospital Analyzer Web.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source hospital_web_env/bin/activate

echo "Starting Hospital Outcomes Analyzer..."
echo "The application will open in your web browser."
echo "Press Ctrl+C to stop the application."
echo ""

# Launch Streamlit app
streamlit run hospital_analyzer_web.py --server.port 8501 --server.headless false
EOF

chmod +x "Hospital Analyzer Web.command"

echo "✓ Web launcher created"

echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the Hospital Outcomes Analyzer Web App:"
echo "1. Double-click 'Hospital Analyzer Web.command' in this folder"
echo "2. The app will open automatically in your web browser"
echo "3. Or manually run: streamlit run hospital_analyzer_web.py"
echo ""
echo "The web interface provides:"
echo "- Interactive charts and graphs"
echo "- Better data visualization"
echo "- Easy export functionality"
echo "- Responsive design"
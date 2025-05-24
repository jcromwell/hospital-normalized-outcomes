#!/bin/bash

# Create Standalone Hospital Analyzer Package

echo "Creating Standalone Hospital Analyzer Package..."
echo "==============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Create package directory
PACKAGE_NAME="Hospital-Analyzer-Standalone"
rm -rf "$PACKAGE_NAME"
mkdir "$PACKAGE_NAME"
cd "$PACKAGE_NAME"

echo "✓ Created package directory"

# Copy application files
cp "../hospital_analyzer_web.py" .
cp "../Readmission CMI-LOS-DRG 329-334 2022.xlsx" .
cp "../requirements_web.txt" .
cp "../README.md" .

echo "✓ Copied application files"

# Create virtual environment
python3 -m venv app_env
source app_env/bin/activate

echo "✓ Created virtual environment"

# Install dependencies
pip install --upgrade pip
pip install -r requirements_web.txt

echo "✓ Installed dependencies"

# Create launcher script that uses bundled environment
cat > "Hospital Analyzer.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

echo "Starting Hospital Outcomes Analyzer..."
echo "======================================"

# Check if virtual environment exists
if [ ! -d "app_env" ]; then
    echo "Error: Application environment not found."
    echo "Please ensure all files are in the same folder."
    exit 1
fi

# Activate virtual environment
source app_env/bin/activate

# Check if data file exists
if [ ! -f "Readmission CMI-LOS-DRG 329-334 2022.xlsx" ]; then
    echo "Error: Data file not found."
    echo "Please ensure 'Readmission CMI-LOS-DRG 329-334 2022.xlsx' is in the same folder."
    exit 1
fi

echo "✓ Environment ready"
echo "✓ Data file found"
echo ""
echo "Opening Hospital Analyzer in your web browser..."
echo "Press Ctrl+C to stop the application."
echo ""

# Launch the app
streamlit run hospital_analyzer_web.py --server.port 8501 --server.headless false --server.address localhost

EOF

chmod +x "Hospital Analyzer.command"

echo "✓ Created launcher script"

# Create simple installer for the recipient
cat > "INSTALL.md" << 'EOF'
# Hospital Outcomes Analyzer - Standalone Package

This package contains everything needed to run the Hospital Outcomes Analyzer.

## Quick Start

1. **Double-click** `Hospital Analyzer.command`
2. The application will open in your web browser automatically
3. **That's it!** No additional installation required.

## System Requirements

- **macOS**: 10.14 (Mojave) or later
- **Python 3**: Pre-installed on modern macOS
- **Web Browser**: Safari, Chrome, Firefox, or Edge

## What's Included

- ✅ Hospital Analyzer web application
- ✅ Complete dataset (2,913 hospitals)
- ✅ All required Python libraries
- ✅ Isolated environment (won't affect your system)

## Features

- Hospital and IDN selection and comparison
- Normalized metrics (ALOS/CMI, Readmission Rate/CMI)
- Interactive charts and visualizations
- Data export to CSV
- Summary statistics and percentile rankings

## Troubleshooting

**"Permission denied" error:**
- Right-click `Hospital Analyzer.command`
- Select "Open" from the menu
- Click "Open" when prompted about unidentified developer

**Application won't start:**
- Ensure all files stay in the same folder
- Don't rename the `app_env` folder
- Make sure you have internet connection for first launch

## File Structure

```
Hospital-Analyzer-Standalone/
├── Hospital Analyzer.command     # Launch this file
├── hospital_analyzer_web.py      # Main application
├── Readmission CMI-LOS-DRG 329-334 2022.xlsx  # Dataset
├── app_env/                      # Python environment (don't modify)
├── README.md                     # Documentation
└── INSTALL.md                    # This file
```

For questions or issues, contact the development team.
EOF

# Create distribution package info
cat > "README_DISTRIBUTION.txt" << 'EOF'
HOSPITAL OUTCOMES ANALYZER - STANDALONE DISTRIBUTION
===================================================

This folder contains a complete, self-contained version of the Hospital Outcomes Analyzer.

TO SHARE WITH COLLEAGUES:
1. Zip this entire folder
2. Send the zip file
3. Recipient extracts and double-clicks "Hospital Analyzer.command"

PACKAGE CONTENTS:
- Web-based application using Streamlit
- Complete hospital dataset for DRG 329-334
- All Python dependencies pre-installed
- Isolated virtual environment
- Cross-platform compatibility (macOS focus)

The recipient needs NO additional software installation.
Just extract and run!

Package size: ~50MB
Created: $(date)
EOF

cd ..

echo ""
echo "✓ Standalone package created successfully!"
echo ""
echo "Package location: $PWD/$PACKAGE_NAME/"
echo ""
echo "TO DISTRIBUTE:"
echo "1. Zip the '$PACKAGE_NAME' folder"
echo "2. Send to your colleague"
echo "3. They extract and double-click 'Hospital Analyzer.command'"
echo ""
echo "NO additional installation required on their end!"
#!/bin/bash
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "hospital_web_env" ]; then
    echo "Virtual environment not found. Creating and setting up..."
    python3 -m venv hospital_web_env
    source hospital_web_env/bin/activate
    pip install --upgrade pip
    pip install -r requirements_web.txt
    echo "Setup complete!"
    echo ""
else
    # Activate existing environment
    source hospital_web_env/bin/activate
    
    # Ensure all requirements are installed
    echo "Checking requirements..."
    pip install -q -r requirements_web.txt
fi

echo "Starting Hospital Outcomes Analyzer..."
echo "The application will open in your web browser."
echo "Press Ctrl+C to stop the application."
echo ""

# Launch Streamlit app
streamlit run hospital_analyzer_web.py --server.port 8501 --server.headless false

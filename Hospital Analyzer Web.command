#!/bin/bash
cd "$(dirname "$0")"
source hospital_web_env/bin/activate

echo "Starting Hospital Outcomes Analyzer..."
echo "The application will open in your web browser."
echo "Press Ctrl+C to stop the application."
echo ""

# Launch Streamlit app
streamlit run hospital_analyzer_web.py --server.port 8501 --server.headless false

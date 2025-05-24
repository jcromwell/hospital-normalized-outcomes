#!/bin/bash
cd "$(dirname "$0")"
source hospital_analyzer_env/bin/activate
python3 hospital_analyzer.py

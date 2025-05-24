# Hospital Outcomes Analyzer

A standalone macOS application for analyzing hospital readmission data for DRG codes 329-334 (major joint replacement procedures).

## Features

- **Hospital Selection**: Choose individual hospitals by Provider ID and name
- **IDN Analysis**: Select and analyze Integrated Delivery Networks
- **Flexible Comparisons**: Compare against all hospitals, same IDN, or same state
- **Multiple Metrics**: Analyze readmission rates, average length of stay (ALOS), and Case Mix Index (CMI)
- **Interactive Charts**: Generate histograms with statistical overlays
- **Data Export**: Export filtered data to Excel or CSV formats
- **Summary Statistics**: View percentile distributions and key metrics

## Installation

### Web App (Recommended)

The web-based version works reliably on all macOS systems:

1. Open Terminal and navigate to this folder
2. Run the web installer:
   ```bash
   ./install_web.sh
   ```
3. Double-click "Hospital Analyzer Web.command" to launch
4. The app opens automatically in your web browser

### Desktop App (Alternative)

If you prefer a desktop application:

1. Install dependencies:
   ```bash
   ./install.sh
   ```
2. Double-click "Hospital Analyzer.command"

**Note**: The desktop version requires tkinter support. If you get tkinter errors, use the web version instead.

## Data

The application includes hospital outcome data for DRG codes 329-334 from 2022, containing:

- **2,913 hospitals** across **678 IDNs**
- **Key metrics**: Readmission rates, ALOS, CMI, discharge volumes
- **Hospital characteristics**: Bed counts, payor mix, geographic location
- **Quality indicators**: Medicare discharge volumes, staffing data

## Usage

1. **Select Index Hospital/IDN**: Choose the hospital or health system you want to analyze
2. **Choose Comparator Group**: Select whether to compare against all hospitals, same IDN, or same state
3. **Update Analysis**: Click to generate summary statistics
4. **View Results**: 
   - **Summary Tab**: Key statistics and percentile rankings
   - **Chart Tab**: Visual distributions with statistical markers
   - **Data Table Tab**: Filtered hospital data
5. **Export Data**: Save filtered results to Excel or CSV

## System Requirements

- **macOS**: 10.14 (Mojave) or later
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM (recommended 1GB)
- **Storage**: 50MB free space

## Troubleshooting

### Common Issues

**"Python 3 not found"**
- Install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

**"Permission denied"**
- Run: `chmod +x install.sh` in Terminal
- Try running installer with: `bash install.sh`

**Application won't start**
- Ensure the Excel data file is in the same folder as the application
- Check that all dependencies are installed: `pip3 list`

### Data Issues

**Missing metrics show as "N/A"**
- Some hospitals have incomplete data in the original dataset
- This is normal and doesn't affect analysis of available metrics

**Unexpected filtering results**
- IDN names may have variations (e.g., "HCA" vs "HCA Healthcare")
- Use the dropdown menus to see exact available values

## Technical Details

- **Framework**: Python Tkinter (native macOS compatibility)
- **Data Processing**: Pandas for Excel/CSV handling
- **Visualization**: Matplotlib with Tkinter integration
- **Packaging**: Self-contained with virtual environment

## Support

For technical issues or feature requests, contact the development team or refer to the application documentation.
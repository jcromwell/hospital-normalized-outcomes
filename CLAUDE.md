# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a standalone Streamlit web application for analyzing hospital readmission data. The application provides an interactive web interface for selecting hospitals/IDNs, comparing metrics, and generating charts and tables from DRG 329-334 data (major joint replacement procedures) from 2022.

## Application Architecture

**Main Application**: `hospital_analyzer_web.py`
- Streamlit-based web interface
- Data loading and cleaning functions
- Interactive hospital/IDN selection
- Chart generation with plotly/matplotlib
- Export functionality

**Key Components**:
- Hospital/IDN selection dropdowns
- Comparator group selection (All, Same IDN, Same State)
- Summary statistics generation
- Interactive data tables
- Chart visualization with percentile overlays

## Data Structure

- `Readmission CMI-LOS-DRG 329-334 2022.xlsx`: Dataset with 2,913 hospitals across 678 IDNs
  - Key metrics: Readmission Rate, ALOS (Average Length of Stay), CMI (Case Mix Index)
  - Hospital identifiers: Provider ID, Hospital name, IDN name
  - Geographic data: City/State for regional comparisons
  - Characteristics: Bed counts, discharge volumes, payor mix

## Development Commands

**Installation**: `./install_web.sh` - Sets up virtual environment and dependencies
**Run Application**: `streamlit run hospital_analyzer_web.py` or double-click "Hospital Analyzer Web.command"
**Install Dependencies**: `pip install -r requirements_web.txt`

## Data Processing Notes

- CMI column requires conversion from object to numeric type
- Missing data is common (ALOS: 1,043 nulls, Readmission Rate: 736 nulls)
- IDN names should be normalized (fill missing with "Independent")
- DRG codes 329-334 are pre-filtered major joint replacement procedures

## Web Framework

Uses Streamlit for rapid web application development with built-in interactivity and deployment options. The application is designed to run locally or be deployed to cloud platforms.
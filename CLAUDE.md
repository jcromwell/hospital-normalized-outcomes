# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a standalone macOS application for analyzing hospital readmission data. The application provides an interactive GUI for selecting hospitals/IDNs, comparing metrics, and generating charts and tables from DRG 329-334 data (major joint replacement procedures) from 2022.

## Application Architecture

**Main Application**: `hospital_analyzer.py`
- Tkinter-based GUI with tabbed interface
- Data loading and cleaning functions
- Interactive hospital/IDN selection
- Chart generation with matplotlib
- Export functionality

**Key Components**:
- Hospital/IDN selection dropdowns
- Comparator group selection (All, Same IDN, Same State)
- Summary statistics generation
- Interactive data tables with scrolling
- Chart visualization with percentile overlays

## Data Structure

- `Readmission CMI-LOS-DRG 329-334 2022.xlsx`: Dataset with 2,913 hospitals across 678 IDNs
  - Key metrics: Readmission Rate, ALOS (Average Length of Stay), CMI (Case Mix Index)
  - Hospital identifiers: Provider ID, Hospital name, IDN name
  - Geographic data: City/State for regional comparisons
  - Characteristics: Bed counts, discharge volumes, payor mix

## Development Commands

**Installation**: `./install.sh` - Sets up virtual environment and dependencies
**Run Application**: `python3 hospital_analyzer.py` or double-click "Hospital Analyzer.command"
**Install Dependencies**: `pip install -r requirements.txt`

## Data Processing Notes

- CMI column requires conversion from object to numeric type
- Missing data is common (ALOS: 1,043 nulls, Readmission Rate: 736 nulls)
- IDN names should be normalized (fill missing with "Independent")
- DRG codes 329-334 are pre-filtered major joint replacement procedures

## GUI Framework

Uses tkinter for maximum macOS compatibility without external GUI dependencies. The application is designed to be self-contained and easily distributable with the dataset.
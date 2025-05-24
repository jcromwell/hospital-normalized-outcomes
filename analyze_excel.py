#!/usr/bin/env python3
"""
Excel File Analysis Script
Analyzes the structure and content of the readmission data Excel file
"""

import pandas as pd
import numpy as np
import sys
import os

def analyze_excel_file(file_path):
    """Analyze Excel file structure and content"""
    
    print(f"Analyzing Excel file: {file_path}")
    print("=" * 60)
    
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return
        
        # Read Excel file to check for multiple sheets
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        print(f"Number of sheets: {len(sheet_names)}")
        print(f"Sheet names: {sheet_names}")
        print("-" * 60)
        
        # Analyze each sheet
        for i, sheet_name in enumerate(sheet_names):
            print(f"\n{'='*20} SHEET {i+1}: '{sheet_name}' {'='*20}")
            
            try:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                print(f"Shape: {df.shape} (rows x columns)")
                print(f"Total cells: {df.shape[0] * df.shape[1]:,}")
                
                # Column information
                print(f"\nColumn Names ({len(df.columns)} total):")
                for j, col in enumerate(df.columns, 1):
                    print(f"  {j:2d}. {col}")
                
                # Data types
                print(f"\nData Types:")
                for col, dtype in df.dtypes.items():
                    non_null_count = df[col].notna().sum()
                    null_count = df[col].isna().sum()
                    print(f"  {col:<40} | {str(dtype):<12} | Non-null: {non_null_count:>6} | Null: {null_count:>6}")
                
                # First few rows
                print(f"\nFirst 5 rows:")
                print(df.head().to_string())
                
                # Basic statistics for numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    print(f"\nNumeric Column Statistics:")
                    print(df[numeric_cols].describe().round(2).to_string())
                
                # Unique values for potential key fields (showing first 20 unique values)
                potential_key_fields = []
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['hospital', 'idn', 'provider', 'facility', 'name', 'id', 'code']):
                        potential_key_fields.append(col)
                
                if potential_key_fields:
                    print(f"\nPotential Key Fields for Hospital/IDN Selection:")
                    for col in potential_key_fields:
                        unique_vals = df[col].dropna().unique()
                        print(f"  {col}:")
                        print(f"    Unique values: {len(unique_vals)}")
                        if len(unique_vals) <= 20:
                            print(f"    Values: {list(unique_vals)}")
                        else:
                            print(f"    Sample values: {list(unique_vals[:10])}... (showing first 10 of {len(unique_vals)})")
                
                # Check for DRG-related columns
                drg_cols = [col for col in df.columns if 'drg' in col.lower()]
                if drg_cols:
                    print(f"\nDRG-related columns:")
                    for col in drg_cols:
                        unique_vals = df[col].dropna().unique()
                        print(f"  {col}: {len(unique_vals)} unique values")
                        if len(unique_vals) <= 10:
                            print(f"    Values: {sorted(unique_vals)}")
                
                # Check for outcome/metric columns
                metric_keywords = ['cmi', 'los', 'length', 'stay', 'readmission', 'rate', 'ratio', 'index', 'score']
                metric_cols = []
                for col in df.columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in metric_keywords):
                        metric_cols.append(col)
                
                if metric_cols:
                    print(f"\nPotential Outcome/Metric Columns:")
                    for col in metric_cols:
                        if df[col].dtype in ['int64', 'float64']:
                            stats = df[col].describe()
                            print(f"  {col}:")
                            print(f"    Range: {stats['min']:.3f} to {stats['max']:.3f}")
                            print(f"    Mean: {stats['mean']:.3f}, Median: {stats['50%']:.3f}")
                        else:
                            unique_vals = df[col].dropna().unique()
                            print(f"  {col}: {len(unique_vals)} unique values")
                
            except Exception as e:
                print(f"Error reading sheet '{sheet_name}': {str(e)}")
                continue
        
        print(f"\n{'='*60}")
        print("ANALYSIS SUMMARY FOR APPLICATION DESIGN:")
        print("="*60)
        print("Key considerations for your application:")
        print("1. Data Structure: Multiple sheets may require sheet selection UI")
        print("2. Hospital Selection: Look for hospital/provider ID and name fields")
        print("3. Filtering: DRG codes 329-334 appear to be the focus")
        print("4. Metrics: CMI (Case Mix Index), LOS (Length of Stay), Readmission rates")
        print("5. Data Types: Mix of categorical and numeric data requiring different handling")
        print("6. Missing Data: Check null counts for data quality considerations")
        
    except Exception as e:
        print(f"ERROR: Failed to analyze file: {str(e)}")
        return

if __name__ == "__main__":
    file_path = "/Users/jcromwell/hospital-normalized-outcomes/Readmission CMI-LOS-DRG 329-334 2022.xlsx"
    analyze_excel_file(file_path)
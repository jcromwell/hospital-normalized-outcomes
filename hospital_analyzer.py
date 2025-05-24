#!/usr/bin/env python3
"""
Hospital Outcomes Analyzer
A standalone application for analyzing hospital readmission data
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import sys

class HospitalAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Outcomes Analyzer - DRG 329-334")
        self.root.geometry("1200x800")
        
        # Data storage
        self.df = None
        self.filtered_df = None
        
        # Load data on startup
        self.load_default_data()
        
        # Create GUI
        self.create_widgets()
        
    def load_default_data(self):
        """Load the default Excel file"""
        data_file = "Readmission CMI-LOS-DRG 329-334 2022.xlsx"
        if os.path.exists(data_file):
            try:
                self.df = pd.read_excel(data_file)
                # Clean the data
                self.clean_data()
            except Exception as e:
                messagebox.showerror("Error", f"Could not load data file: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"Data file '{data_file}' not found in current directory")
    
    def clean_data(self):
        """Clean and prepare the data"""
        if self.df is not None:
            # Convert CMI to numeric
            self.df['CMI'] = pd.to_numeric(self.df['CMI'], errors='coerce')
            
            # Remove empty columns
            self.df = self.df.dropna(axis=1, how='all')
            
            # Fill missing IDN values
            self.df['IDN'] = self.df['IDN'].fillna('Independent')
            
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Selection Frame
        selection_frame = ttk.LabelFrame(main_frame, text="Hospital Selection", padding="10")
        selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Index Hospital Selection
        ttk.Label(selection_frame, text="Index Hospital:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.index_hospital_var = tk.StringVar()
        self.index_hospital_combo = ttk.Combobox(selection_frame, textvariable=self.index_hospital_var, width=50)
        self.index_hospital_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # IDN Selection
        ttk.Label(selection_frame, text="Index IDN:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.index_idn_var = tk.StringVar()
        self.index_idn_combo = ttk.Combobox(selection_frame, textvariable=self.index_idn_var, width=50)
        self.index_idn_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Comparator Selection
        ttk.Label(selection_frame, text="Compare to:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        self.comparator_var = tk.StringVar(value="All Hospitals")
        comparator_frame = ttk.Frame(selection_frame)
        comparator_frame.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(comparator_frame, text="All Hospitals", variable=self.comparator_var, 
                       value="All Hospitals").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(comparator_frame, text="Same IDN", variable=self.comparator_var, 
                       value="Same IDN").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Radiobutton(comparator_frame, text="Same State", variable=self.comparator_var, 
                       value="Same State").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(selection_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Update Analysis", command=self.update_analysis).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Export Data", command=self.export_data).grid(row=0, column=1, padx=(5, 0))
        
        # Analysis Frame
        analysis_frame = ttk.LabelFrame(main_frame, text="Analysis", padding="10")
        analysis_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Metric Selection
        ttk.Label(analysis_frame, text="Metric:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.metric_var = tk.StringVar(value="Readmission Rate")
        metric_combo = ttk.Combobox(analysis_frame, textvariable=self.metric_var, 
                                   values=["Readmission Rate", "ALOS", "CMI"], width=20)
        metric_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Button(analysis_frame, text="Create Chart", command=self.create_chart).grid(row=0, column=2, padx=(10, 0))
        
        # Results Frame (Notebook for tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary Tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        self.summary_text = tk.Text(self.summary_frame, wrap=tk.WORD)
        summary_scrollbar = ttk.Scrollbar(self.summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        summary_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(0, weight=1)
        
        # Chart Tab
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Chart")
        
        # Data Tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Table")
        
        # Initialize data
        self.populate_dropdowns()
        
    def populate_dropdowns(self):
        """Populate the dropdown menus with data"""
        if self.df is not None:
            # Hospital dropdown
            hospitals = [f"{row['Provider']} - {row['Hospital']}" for _, row in self.df.iterrows() if pd.notna(row['Hospital'])]
            self.index_hospital_combo['values'] = sorted(hospitals)
            
            # IDN dropdown
            idns = self.df['IDN'].dropna().unique()
            self.index_idn_combo['values'] = sorted(idns)
            
    def update_analysis(self):
        """Update the analysis based on current selections"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        # Get selected hospital/IDN
        selected_hospital = self.index_hospital_var.get()
        selected_idn = self.index_idn_var.get()
        
        if not selected_hospital and not selected_idn:
            messagebox.showwarning("Warning", "Please select a hospital or IDN")
            return
            
        # Filter data based on comparator selection
        comparator = self.comparator_var.get()
        
        if selected_hospital:
            provider_id = selected_hospital.split(' - ')[0]
            index_data = self.df[self.df['Provider'].astype(str) == provider_id]
        else:
            index_data = self.df[self.df['IDN'] == selected_idn]
            
        if index_data.empty:
            messagebox.showwarning("Warning", "No data found for selection")
            return
            
        # Get comparator data
        if comparator == "All Hospitals":
            comparator_data = self.df
        elif comparator == "Same IDN":
            if selected_hospital:
                idn = index_data.iloc[0]['IDN']
                comparator_data = self.df[self.df['IDN'] == idn]
            else:
                comparator_data = self.df[self.df['IDN'] == selected_idn]
        elif comparator == "Same State":
            if selected_hospital:
                state = index_data.iloc[0]['City/State'].split(', ')[-1] if pd.notna(index_data.iloc[0]['City/State']) else None
                if state:
                    comparator_data = self.df[self.df['City/State'].str.contains(state, na=False)]
                else:
                    comparator_data = self.df
            else:
                comparator_data = self.df
                
        # Generate summary
        self.generate_summary(index_data, comparator_data)
        
        # Update data table
        self.update_data_table(comparator_data)
        
    def generate_summary(self, index_data, comparator_data):
        """Generate summary statistics"""
        summary = []
        
        if not index_data.empty:
            summary.append("INDEX HOSPITAL/IDN STATISTICS:")
            summary.append("=" * 40)
            
            if len(index_data) == 1:
                row = index_data.iloc[0]
                summary.append(f"Hospital: {row['Hospital']}")
                summary.append(f"Provider ID: {row['Provider']}")
                summary.append(f"IDN: {row['IDN']}")
                summary.append(f"Location: {row['City/State']}")
                summary.append(f"Staffed Beds: {row['Number of Staffed Beds']}")
                summary.append("")
                
                summary.append("KEY METRICS:")
                summary.append(f"Readmission Rate: {row['Readmission Rate']:.1%}" if pd.notna(row['Readmission Rate']) else "Readmission Rate: N/A")
                summary.append(f"Average LOS: {row['ALOS']:.1f} days" if pd.notna(row['ALOS']) else "Average LOS: N/A")
                summary.append(f"CMI: {row['CMI']:.2f}" if pd.notna(row['CMI']) else "CMI: N/A")
            else:
                summary.append(f"IDN: {index_data.iloc[0]['IDN']}")
                summary.append(f"Number of Hospitals: {len(index_data)}")
                summary.append("")
                
                summary.append("AGGREGATE METRICS:")
                summary.append(f"Avg Readmission Rate: {index_data['Readmission Rate'].mean():.1%}" if not index_data['Readmission Rate'].isna().all() else "Avg Readmission Rate: N/A")
                summary.append(f"Avg ALOS: {index_data['ALOS'].mean():.1f} days" if not index_data['ALOS'].isna().all() else "Avg ALOS: N/A")
                summary.append(f"Avg CMI: {index_data['CMI'].mean():.2f}" if not index_data['CMI'].isna().all() else "Avg CMI: N/A")
            
        summary.append("\n")
        summary.append("COMPARATOR GROUP STATISTICS:")
        summary.append("=" * 40)
        summary.append(f"Number of Hospitals: {len(comparator_data)}")
        summary.append("")
        
        # Percentile calculations
        for metric, column in [("Readmission Rate", "Readmission Rate"), ("ALOS", "ALOS"), ("CMI", "CMI")]:
            clean_data = comparator_data[column].dropna()
            if not clean_data.empty:
                summary.append(f"{metric.upper()} DISTRIBUTION:")
                summary.append(f"  Mean: {clean_data.mean():.2f}")
                summary.append(f"  Median: {clean_data.median():.2f}")
                summary.append(f"  25th Percentile: {clean_data.quantile(0.25):.2f}")
                summary.append(f"  75th Percentile: {clean_data.quantile(0.75):.2f}")
                summary.append(f"  Min: {clean_data.min():.2f}")
                summary.append(f"  Max: {clean_data.max():.2f}")
                summary.append("")
        
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', '\n'.join(summary))
        
    def update_data_table(self, data):
        """Update the data table with filtered results"""
        # Clear existing table
        for widget in self.data_frame.winfo_children():
            widget.destroy()
            
        if data.empty:
            ttk.Label(self.data_frame, text="No data to display").pack()
            return
            
        # Create treeview
        columns = ['Provider', 'Hospital', 'IDN', 'City/State', 'Readmission Rate', 'ALOS', 'CMI', 'Number of Staffed Beds']
        tree = ttk.Treeview(self.data_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
            
        # Add data
        for _, row in data.iterrows():
            values = []
            for col in columns:
                value = row[col]
                if col == 'Readmission Rate' and pd.notna(value):
                    values.append(f"{value:.1%}")
                elif col in ['ALOS', 'CMI'] and pd.notna(value):
                    values.append(f"{value:.2f}")
                else:
                    values.append(str(value) if pd.notna(value) else "N/A")
            tree.insert('', 'end', values=values)
            
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(self.data_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.rowconfigure(0, weight=1)
        
    def create_chart(self):
        """Create a chart based on selected metric"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        metric = self.metric_var.get()
        comparator = self.comparator_var.get()
        
        # Get data
        if comparator == "All Hospitals":
            plot_data = self.df
            title_suffix = "All Hospitals"
        elif comparator == "Same IDN":
            selected_idn = self.index_idn_var.get()
            if selected_idn:
                plot_data = self.df[self.df['IDN'] == selected_idn]
                title_suffix = f"IDN: {selected_idn}"
            else:
                plot_data = self.df
                title_suffix = "All Hospitals"
        else:
            plot_data = self.df
            title_suffix = "All Hospitals"
            
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot histogram
        data_column = metric if metric != "Readmission Rate" else "Readmission Rate"
        clean_data = plot_data[data_column].dropna()
        
        if not clean_data.empty:
            ax.hist(clean_data, bins=30, alpha=0.7, edgecolor='black')
            ax.set_xlabel(metric)
            ax.set_ylabel('Number of Hospitals')
            ax.set_title(f'{metric} Distribution - {title_suffix}')
            ax.grid(True, alpha=0.3)
            
            # Add statistics
            mean_val = clean_data.mean()
            median_val = clean_data.median()
            ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
            ax.axvline(median_val, color='blue', linestyle='--', label=f'Median: {median_val:.2f}')
            ax.legend()
            
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def export_data(self):
        """Export filtered data to Excel"""
        if self.df is None:
            messagebox.showwarning("Warning", "No data to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.csv'):
                    self.df.to_csv(filename, index=False)
                else:
                    self.df.to_excel(filename, index=False)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export data: {str(e)}")

def main():
    root = tk.Tk()
    app = HospitalAnalyzer(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
# ESPPF Incubation Log Analyzer

A Python-based desktop application for analyzing and visualizing incubation data from embryo incubators. This tool processes CSV log files to generate comprehensive statistics and interactive charts, making it easier to monitor and analyze incubation parameters over time.

## Overview

The ESPPF Incubation Log Analyzer is designed to help embryologists and laboratory staff monitor and analyze critical parameters from embryo incubation systems. It provides an intuitive graphical interface for:
- Loading and processing incubation log files
- Calculating statistical metrics over specified time periods
- Generating detailed visualizations of key parameters
- Monitoring system performance and environmental conditions

## Key Features

### Data Analysis
- Processes multiple CSV log files from incubation systems
- Calculates comprehensive statistics including min, max, average, median, and standard deviation for:
  - Temperature control
  - CO₂ concentration and flow
  - O₂ concentration
  - N₂ pressure and flow
  - System parameters (UV light, chamber temperatures, etc.)

### Visualization
- Interactive multi-panel charts showing:
  - Temperature trends with setpoints
  - CO₂ concentration, pressure, and flow rates
  - O₂ levels and N₂ system parameters
- Real-time visualization of:
  - Door opening events
  - System alarms
  - Parameter deviations

### User Interface
- Clean, intuitive Qt-based interface
- Easy file selection and data import
- Customizable date range selection
- Real-time statistical calculations
- Export capabilities for further analysis

## Technical Details

- Built with Python 3.x
- Uses PySide2 for the graphical interface
- Leverages pandas for data processing
- Matplotlib for scientific visualization
- Handles large datasets efficiently with memory management

## Requirements

The application requires Python 3.x and several dependencies:
- PySide2
- pandas
- matplotlib
- numpy
- tabulate

A complete list of dependencies is available in the requirements.txt file.

## Usage

1. Launch the application
2. Browse and select a folder containing incubation log CSV files
3. Enter the instrument number for identification
4. Specify the time range for analysis
5. Generate statistics and visualizations with a single click

## Version

Current version: 1.2.1 (February 2025)
- Enhanced memory management
- Improved visualization features
- Added comprehensive system parameter monitoring

---

*Note: This tool is designed for processing specific CSV log file formats from embryo incubation systems. Please ensure your input data matches the expected format.*


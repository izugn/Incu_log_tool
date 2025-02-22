# Incubation Log Analyzer

A Python-based desktop application for analyzing and visualizing sensor datalog of a specific [incubator](https://www.vitrolife.com/products/time-lapse-systems/embryoscopeplus-time-lapse-system/). This tool processes CSV log files to generate comprehensive statistics and interactive charts for initial root cause analysis, making it easier to catch deviations, sensor malfunctions and to monitor incubation parameters over time.

The main purpose of this software tool is to help helpdesk agents and service technicians daily work with troubleshooting the device in question.
It provides an intuitive graphical interface for:
- Fast loading and processing big incubation log files (Sensor readings 1/min; Monthly log: 40K+ row CSV);
- Calculating statistical metrics over specified time periods;
- Generating detailed visualizations of key parameters (sensor readings, alarm state, incubator door openings).

## Key Features

### Data Analysis
- Processes multiple CSV log files from incubation systems
- Calculates statistics including min, max, average, median, and standard deviation for:
  - Temperature control
  - CO₂ concentration and flow
  - O₂ concentration
  - N₂ pressure and flow
  - System parameters (UV light, chamber temperatures, etc.)

### Visualization
- Interactive (matplotlib) multi-panel charts showing:
  - Temperature trends with setpoints
  - CO₂ concentration, pressure, and flow rates
  - O₂ levels and N₂ system parameters
- Visualization of events like 'door opening' and sensor alarms gives further hint to quickly catch the root cause.

### User Interface
- Clean, intuitive Qt-based interface
- Data Source folder selection and data import
- Customizable date range selection for statistic generation
- Export capabilities for further deviation report records.

![gui_1](https://github.com/user-attachments/assets/03ee31c6-1549-41af-a60f-bb129f62fbeb)

![matplot_chart_1](https://github.com/user-attachments/assets/fbd67f75-2e95-46cc-86d5-687b5313cda2)


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

## Usage

1. Launch the application
2. Browse and select a folder containing incubation log CSV files
3. Enter the instrument number for identification
4. Specify the time range for statistics
5. Generate statistics and visualizations with a single click.

---



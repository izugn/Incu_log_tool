import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import axes
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from tabulate import tabulate
tabulate.PRESERVE_WHITESPACE = True
from PySide2.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QTextEdit, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFormLayout, QMessageBox)
from PySide2.QtGui import QFont, QIcon, QTextDocument
from PySide2.QtCore import Qt, QSize
from matplotlib.ticker import FuncFormatter
import gc # garbage collector

__version__ = '1.2.1-20250216'

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ESPPF Incubation-log Analyzer v.{__version__}")
        self.setMinimumSize(680, 580)  # Set minimum window size
        self.setWindowIcon(QIcon(resource_path('icon.ico')))
        self.initUI()


    def initUI(self):
        # Create a central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Browse section
        browse_button = QPushButton('Browse incubation report CSV files')
        browse_button.clicked.connect(self.browse_folder)
        main_layout.addWidget(browse_button)
        
        # Form layout for instrument and date inputs
        form_layout = QFormLayout()
        
        # Instrument input
        self.instrument_input = QLineEdit()
        self.instrument_input.setPlaceholderText('Instrument nr.')
        self.instrument_input.setFixedWidth(100)
        form_layout.addRow('Instrument nr.(ixxxx):', self.instrument_input)
        
        # Date input label
        date_label = QLabel('Define a timeframe for incubation log statistics.(YYYY-MM-DD hh:mm):')
        form_layout.addRow(date_label)
        
        # Date inputs in horizontal layout
        date_layout = QHBoxLayout()
        self.start_date_input = QLineEdit()
        self.start_date_input.setPlaceholderText('Start date&time')
        self.end_date_input = QLineEdit()
        self.end_date_input.setPlaceholderText('End date&time')
        date_layout.addWidget(self.start_date_input)
        date_layout.addWidget(self.end_date_input)
        form_layout.addRow(date_layout)
        
        main_layout.addLayout(form_layout)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        calculate_button = QPushButton('Calculate Statistics')
        calculate_button.clicked.connect(self.calculate_statistics)
        generate_charts_button = QPushButton('Generate Charts')
        generate_charts_button.clicked.connect(self.generate_charts)
        button_layout.addWidget(calculate_button)
        button_layout.addWidget(generate_charts_button)
        main_layout.addLayout(button_layout)
        
        # Stats text edit
        self.stats_text_edit = QTextEdit()
        self.stats_text_edit.setReadOnly(True)
        monospaced_font = QFont("Consolas", 9)
        self.stats_text_edit.setFont(monospaced_font)
        self.stats_text_edit.textChanged.connect(self.adjust_window_size)
        main_layout.addWidget(self.stats_text_edit)
        
        # Set layout spacing and margins
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

    def adjust_window_size(self):
        # Calculate required size for text content
        doc = self.stats_text_edit.document()
        doc_size = doc.size().toSize()
        
        # Add margins and padding
        content_margin = 20  # Additional margin for content
        min_height = 580    # Minimum window height
        
        # Calculate new window size
        new_width = max(640, doc_size.width() + content_margin)
        new_height = max(min_height, 
                        doc_size.height() + 200)  # 200 is space for other widgets
        
        # Set new window size
        self.resize(new_width, new_height)
        
    def setText(self, text):
        # Override setText to ensure proper resizing
        self.stats_text_edit.setText(text)
        self.adjust_window_size()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.concatenate_csv(folder)

    def concatenate_csv(self, folder):
        all_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.csv')]
        header = [
            'Time', 'Embryo Temp. Setpoint', 'Embryo Temp. Avg', 'Temp. Sensor A Avg',
            'Temp. Sensor B Avg', 'Baseplate Temp.', 'Incubator Board Temp.',
            'Bottom Chamber Temp.', 'Backside Temp.', 'Top Chamber Temp.',
            'CO2 Setpoint', 'CO2 Concentration Avg', 'CO2 Pressure Avg',
            'CO2 Flow Avg', 'O2 Setpoint', 'O2 Concentration Avg', 'O2 Regulator On',
            'N2 Pressure Avg', 'N2 Flow Avg', 'UV Light Voltage [mV]',
            'Temp. Alarm Duration [min]', 'CO2 Alarm Duration [min]',
            'O2 Alarm Duration [min]', 'Door Open Duration [s]'
        ]
        dtype = {
        'Embryo Temp. Setpoint': 'float32', 'Embryo Temp. Avg': 'float32',
        'Temp. Sensor A Avg': 'float32', 'Temp. Sensor B Avg': 'float32', 'Baseplate Temp.': 'float32',
        'Incubator Board Temp.': 'float32', 'Bottom Chamber Temp.': 'float32', 'Backside Temp.': 'float32',
        'Top Chamber Temp.': 'float32', 'CO2 Setpoint': 'float32', 'CO2 Concentration Avg': 'float32',
        'CO2 Pressure Avg': 'float32', 'CO2 Flow Avg': 'float32', 'O2 Setpoint': 'float32',
        'O2 Concentration Avg': 'float32', 'O2 Regulator On': 'bool', 'N2 Pressure Avg': 'float32',
        'N2 Flow Avg': 'float32', 'UV Light Voltage [mV]': 'float32',
        'Temp. Alarm Duration [min]': 'float32', 'CO2 Alarm Duration [min]': 'float32',
        'O2 Alarm Duration [min]': 'float32', 'Door Open Duration [s]': 'float32'
        }
        # Read all CSV files in the folder and concatenate them into a single dataframe
        # The 'Time' column is parsed as a datetime object and the header is set to the defined header
        # The 'dtype' parameter is used to specify the data types of the columns
        df_list = [pd.read_csv(f, sep=';', names=header, header=0, dtype=dtype, parse_dates=['Time']) for f in all_files]
        raw_df = pd.concat(df_list, ignore_index=True)
        
        # Just floor to minutes after parsing
        raw_df['Time'] = raw_df['Time'].dt.floor('min')
    
        # Sort and remove duplicates
        raw_df = raw_df.sort_values(by='Time').drop_duplicates(subset='Time').reset_index(drop=True)
        
        # copy raw_df as 'combined_df' for further processing: incubation statistics and graphs
        combined_df = raw_df.copy()

        
        ### combined_df now contains the concatenated data with the defined header
        # introduce a new columns, convert them to boolean: 'temp_alarm', 'co2_alarm', 'o2_alarm', 'door_open', based on the alarm durations and door open duration;
        combined_df['temp_alarm'] = combined_df['Temp. Alarm Duration [min]'].apply(lambda x: 1 if x > 0 else 0).astype(bool)
        combined_df['co2_alarm'] = combined_df['CO2 Alarm Duration [min]'].apply(lambda x: 1 if x > 0 else 0).astype(bool)
        combined_df['o2_alarm'] = combined_df['O2 Alarm Duration [min]'].apply(lambda x: 1 if x > 0 else 0).astype(bool)
        combined_df['door_open'] = combined_df['Door Open Duration [s]'].apply(lambda x: 1 if x > 0 else 0).astype(bool)
                
        # Drop columns that are not needed for the incubation stats and graphs
        combined_df = combined_df.drop(columns=['Temp. Sensor A Avg', 'Temp. Sensor B Avg', 'Temp. Alarm Duration [min]', 'CO2 Alarm Duration [min]',
                                                'O2 Alarm Duration [min]', 'Door Open Duration [s]', 'UV Light Voltage [mV]', 'Incubator Board Temp.', 'Baseplate Temp.',
                                                'Bottom Chamber Temp.', 'Backside Temp.', 'Top Chamber Temp.'])
        
 
        # copy combined_df as 'combinded_other' for further processing: Stats of 'Other tab'
        combined_other = raw_df.copy()
        # Drop columns that are not needed for the 'Other' tab stats
        combined_other = combined_other.drop(columns=['Embryo Temp. Setpoint', 'Embryo Temp. Avg', 'CO2 Setpoint', 'CO2 Concentration Avg', 'CO2 Pressure Avg',
            'CO2 Flow Avg', 'O2 Setpoint', 'O2 Concentration Avg', 'O2 Regulator On', 'N2 Pressure Avg', 'N2 Flow Avg', 'Temp. Alarm Duration [min]',
             'CO2 Alarm Duration [min]', 'O2 Alarm Duration [min]', 'Door Open Duration [s]'])
        
        # Delete raw_df to free up memory
        del raw_df

        # Force garbage collection
        gc.collect()

        # Store the combined dataframe in the class instance
        self.combined_df = combined_df
        self.combined_other = combined_other
                
        # Display the data range in the stats_text_edit text field
        data_range_min = combined_df['Time'].min().strftime('%Y-%m-%d %H:%M')
        data_range_max = combined_df['Time'].max().strftime('%Y-%m-%d %H:%M')
        self.stats_text_edit.setText(f"Incubation log date-range:\n\nfrom {data_range_min} to {data_range_max}\n-----------------------------------------\nPick a valid timeframe for calculating statistics.")

        

    def calculate_statistics(self):
        # Check if self.instrument_input is empty or not defined
        if not self.instrument_input.text():
            QMessageBox.critical(self, "Missing Data", "Enter the instrument number.")
            return
                
        # Check if combined_df is defined
        if not hasattr(self, 'combined_df'):
            QMessageBox.critical(self, "Missing Data", "Missing incubation report input data.\nBrowse and select a folder with valid incubation report .CSV files.")
            return
        
        # Check if combined_df is empty or not generated yet
        if self.combined_df is None or self.combined_df.empty:
            QMessageBox.critical(self, "Missing Data", "Missing incubation report input data.")
            return
        instrument_nr = self.instrument_input.text()
        filter_start = self.start_date_input.text()
        filter_end = self.end_date_input.text()

        # Check if start date or end date is empty or null
        if not filter_start or not filter_end:
            QMessageBox.critical(self, "Invalid Date Range", "Enter valid date and time in the format YYYY-MM-DD hh:mm.")
            return


        # Validate date inputs
        try:
            filter_start = pd.to_datetime(filter_start, format='%Y-%m-%d %H:%M')
            filter_end = pd.to_datetime(filter_end, format='%Y-%m-%d %H:%M')
        except ValueError:
            QMessageBox.critical(self, "Invalid Date Format", "Enter valid date and time in the format YYYY-MM-DD hh:mm.")
            return

        # Check if start date is less than end date
        if filter_start >= filter_end:
            QMessageBox.critical(self, "Invalid Date Range", "Start date must be less than end date.")
            return

        # Check if the date range is within the bounds of the data
        input_range_min = self.combined_df['Time'].min()
        input_range_max = self.combined_df['Time'].max()
        if filter_start < input_range_min or filter_end > input_range_max:
            QMessageBox.critical(self, "Invalid Date Range", f"Enter a valid date range between {input_range_min} and {input_range_max}.")
            return

        if self.combined_df is not None and filter_start and filter_end:            
            # Filter self.combined_df based on the dates
            filtered_df = self.combined_df[(self.combined_df['Time'] >= filter_start) & (self.combined_df['Time'] <= filter_end)]
            if filtered_df.empty:
                QMessageBox.critical(self, "No Data", "No data available for the specified date range.")
                return
            temp = filtered_df['Embryo Temp. Avg'].round(2)
            temp_sp = filtered_df['Embryo Temp. Setpoint'].iloc[-1]
            co2_conc = filtered_df['CO2 Concentration Avg'].round(2)
            co2_sp = filtered_df['CO2 Setpoint'].iloc[-1]
            co2_press = filtered_df['CO2 Pressure Avg'].round(2)
            co2_flow = filtered_df['CO2 Flow Avg'].round(2)
            o2_conc = filtered_df['O2 Concentration Avg'].round(2)
            o2_sp = filtered_df['O2 Setpoint'].iloc[-1]
            n2_press = filtered_df['N2 Pressure Avg'].round(2)
            n2_flow = filtered_df['N2 Flow Avg'].round(2)

            stats_to_export = [
                ['Temperature(°C)', temp.min(), temp.max(), temp.mean(), temp.median(), temp.std(), temp_sp],
                ['CO2 conc.(%)', co2_conc.min(), co2_conc.max(), co2_conc.mean(), co2_conc.median(), co2_conc.std(), co2_sp],                
                ['CO2 flow(l/h)', co2_flow.min(), co2_flow.max(), co2_flow.mean(), co2_flow.median(), co2_flow.std()],
                ['CO2 press.(bar)', co2_press.min(), co2_press.max(), co2_press.mean(), co2_press.median(), co2_press.std()],
                ['O2 conc.(%)', o2_conc.min(), o2_conc.max(), o2_conc.mean(), o2_conc.median(), o2_conc.std(), o2_sp],                
                ['N2 flow(l/h)', n2_flow.min(), n2_flow.max(), n2_flow.mean(), n2_flow.median(), n2_flow.std()],
                ['N2 press.(bar)', n2_press.min(), n2_press.max(), n2_press.mean(), n2_press.median(), n2_press.std()]
            ]
            # Filter self.combined_other based on the dates
            filtered_other_df = self.combined_other[(self.combined_other['Time'] >= filter_start) & (self.combined_other['Time'] <= filter_end)]
            inc_board_temp = filtered_other_df['Incubator Board Temp.'].round(2)
            baseplate_temp = filtered_other_df['Baseplate Temp.'].round(2)
            bottom_chamber_temp = filtered_other_df['Bottom Chamber Temp.'].round(2)
            backside_temp = filtered_other_df['Backside Temp.'].round(2)
            top_chamber_temp = filtered_other_df['Top Chamber Temp.'].round(2)
            UV_light_voltage = filtered_other_df['UV Light Voltage [mV]'].round(2)
            temp_sensor_A = filtered_other_df['Temp. Sensor A Avg'].round(2)
            temp_sensor_B = filtered_other_df['Temp. Sensor B Avg'].round(2)

            other_stats_to_export = [                
                ['Baseplate Temp.(°C)', baseplate_temp.min(), baseplate_temp.max(), baseplate_temp.mean(), baseplate_temp.median(), baseplate_temp.std()],
                ['Incubator Board Temp.(°C)', inc_board_temp.min(), inc_board_temp.max(), inc_board_temp.mean(), inc_board_temp.median(), inc_board_temp.std()],
                ['Bottom Chamber Temp.(°C)', bottom_chamber_temp.min(), bottom_chamber_temp.max(), bottom_chamber_temp.mean(), bottom_chamber_temp.median(), bottom_chamber_temp.std()],                
                ['Backside Temp.(°C)', backside_temp.min(), backside_temp.max(), backside_temp.mean(), backside_temp.median(), backside_temp.std()],
                ### Add the following lines to the 'other_stats_to_export' list:
                ## 'Temp. Sensor A Avg', 'Temp. Sensor B Avg'
                ['Temp. Sensor A Avg(°C)', temp_sensor_A.min(), temp_sensor_A.max(), temp_sensor_A.mean(), temp_sensor_A.median(), temp_sensor_A.std()],
                ['Temp. Sensor B Avg(°C)', temp_sensor_B.min(), temp_sensor_B.max(), temp_sensor_B.mean(), temp_sensor_B.median(), temp_sensor_B.std()],
                ['Top Chamber Temp.(°C)', top_chamber_temp.min(), top_chamber_temp.max(), top_chamber_temp.mean(), top_chamber_temp.median(), top_chamber_temp.std()],                
                ['UV Light Voltage (mV)', UV_light_voltage.min(), UV_light_voltage.max(), UV_light_voltage.mean(), UV_light_voltage.median(), UV_light_voltage.std()]
            ]

            # Combine both statistics lists with a separator
            separator = ['-----------------------------']  # Adjust the number of columns as needed
            combined_stats_to_export = stats_to_export + [separator] + other_stats_to_export


            # Column extraction and statistics calculation
            if self.combined_df is not None:
                try:
                    # Use the 'tabulate' library to create a formatted table string from 'stats_to_export'
                    # The headers are set to represent different statistical measures
                    # The table format is set to "simple" and float numbers are formatted to 2 decimal places
                    stat_headers = ['Sensor', 'MIN', 'MAX', 'AVG', 'Median', 'Std', 'SP']            
                    
                    # Create the combined statistics table
                    combined_stats = tabulate(combined_stats_to_export, stat_headers, tablefmt="simple", numalign="decimal", floatfmt=".2f")

                    # Set the formatted stats as the text of the QTextEdit widget
                    self.setText(f"Incubation log statistics; {instrument_nr}\nSeleceted timeframe: {filter_start} - {filter_end}\n\n{combined_stats}")
                    
                    
                except Exception as e:
                    self.stats_text_edit.setText(f"Error in processing: {str(e)}")

#### generate_charts_button.clicked action is defined below:

# combined_df columns with their index numbers:
        # 0: 'Time'
        # 1: 'Embryo Temp. Setpoint'
        # 2: 'Embryo Temp. Avg'
        # 3: 'CO2 Setpoint'
        # 4: 'CO2 Concentration Avg'
        # 5: 'CO2 Pressure Avg'
        # 6: 'CO2 Flow Avg'
        # 7: 'O2 Setpoint'
        # 8: 'O2 Concentration Avg'
        # 9: 'O2 Regulator On'
        # 10: 'N2 Pressure Avg'
        # 11: 'N2 Flow Avg'
        # 12: 'temp_alarm'
        # 13: 'co2_alarm'
        # 14: 'o2_alarm'
        # 15: 'door_open'
     
    
    def generate_charts(self):
        # Check if combined_df is defined
        if not hasattr(self, 'combined_df'):
            QMessageBox.critical(self, "Missing Data", "Missing incubation report input data.")
            return

        # Define the chart range based on the data; min and max values of the 'Time' column
        chart_range_min = self.combined_df['Time'].min().strftime('%Y-%m-%d %H:%M')
        chart_range_max = self.combined_df['Time'].max().strftime('%Y-%m-%d %H:%M')
        instrument_nr = self.instrument_input.text()
        # Create a new figure and specify the number of rows and columns for subplots
        fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1, 2, 2]}, num=(f'Incubation data; instrument nr. {instrument_nr}.'))
        
        # Define a formatter function for the Y-axis ticks
        def y_axis_formatter(x, pos):
            return f'{x:.1f}'

        # Plot 1 Temperature (Embryo Temp. Avg; + SP):
        axes[0].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[1]], label=self.combined_df.columns[1], color='#4a4a4a', linewidth=0.75, linestyle='dashed')
        axes[0].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[2]], label=self.combined_df.columns[2], color='#3232a8', linewidth=0.75)
        axes[0].set_ylabel('Temp.°C')
        axes[0].set_title(f'Incubation data; instrument nr. {instrument_nr}; From {chart_range_min} to {chart_range_max}')
        axes[0].tick_params(axis='y', labelsize=7)  # Change the tick font size on the left Y-axis
        

        # Plot 2: CO2 SP, CO2 conc.; CO2 Flow
        axes[1].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[3]], label=self.combined_df.columns[3], color='#4a4a4a', linewidth=0.75, linestyle='dashed')
        axes[1].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[4]], label=self.combined_df.columns[4], color='#3232a8', linewidth=0.75)
        axes[1].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[6]], label=self.combined_df.columns[6], color='#73f707', linewidth=0.75)
        axes[1].set_ylabel('Co2 conc.(%) / Flow(l/h)')        
        axes[1].tick_params(axis='y', labelsize=7)  # Change the tick font size on the left Y-axis
        axes[1].yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  # Set the number format for the left Y-axis
        
        #### Apply top-padding on the left Y-axis as a percentage of the chart height
        # if the highest value of CO2 flow is higher than CO2 conc.: apply padding based on CO2 flow
        # if the highest value of CO2 conc. is higher than CO2 flow: apply padding based on CO2 conc.
        if self.combined_df[self.combined_df.columns[4]].max() > self.combined_df[self.combined_df.columns[6]].max():
            co2_scale_max = self.combined_df[self.combined_df.columns[4]].max()
        else:
            co2_scale_max = self.combined_df[self.combined_df.columns[6]].max()
        axes[1].set_ylim(top=(co2_scale_max * 1.3)) # add 30% padding on top of the highest value

        # Create a secondary y-axis for CO2 Pressure
        axes_secy1 = axes[1].twinx()
        axes_secy1.plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[5]], label=self.combined_df.columns[5], color='#eb34d8', linewidth=0.75)
        axes_secy1.set_ylabel('Co2 Pressure (bar)')
        # Set the y-axis limits with some padding below zero to elevate scale and separate from conc and flow.
        axes_secy1.set_ylim(-1.5, 0.9)  
        # Define custom tick positions for CO2 Pressure
        axes_secy1.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])  # Adjust values based on data range
        axes_secy1.tick_params(axis='y', labelsize=7)
        
        

        # Plot 3: O2 SP; O2 conc.; N2 Flow
        axes[2].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[7]], label=self.combined_df.columns[7], color='#4a4a4a', linewidth=0.75, linestyle='dashed')
        axes[2].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[8]], label=self.combined_df.columns[8], color='#3232a8', linewidth=0.75)
        axes[2].plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[11]], label=self.combined_df.columns[11], color='#73f707', linewidth=0.75)
        axes[2].set_ylabel('O2 conc.(%) / N2 Flow(l/h)')        
        axes[2].tick_params(axis='y', labelsize=7)  # Change the tick font size on the left Y-axis
        axes[2].yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  # Set the number format for the left Y-axis
        
        #### Apply top-padding on the left Y-axis as a percentage of the chart height
        # if the highest value of N2 flow is higher than O2 conc.: apply padding based on N2 flow
        # if the highest value of O2 conc. is higher than N2 flow: apply padding based on O2 conc.
        if self.combined_df[self.combined_df.columns[8]].max() > self.combined_df[self.combined_df.columns[11]].max():
            O2_scale_max = self.combined_df[self.combined_df.columns[8]].max()
        else:
            O2_scale_max = self.combined_df[self.combined_df.columns[11]].max()        
        axes[2].set_ylim(top=(O2_scale_max * 1.3)) # add 30% padding on top of the highest value

       
        # Create a secondary y-axis for N2 Pressure
        axes_secy2 = axes[2].twinx()
        axes_secy2.plot(self.combined_df[self.combined_df.columns[0]], self.combined_df[self.combined_df.columns[10]], label=self.combined_df.columns[10], color='#eb34d8', linewidth=0.75)
        axes_secy2.set_ylabel('N2 Pressure (bar)')
        # Set the y-axis limits with some padding below zero to elevate scale and separate from conc and flow.
        axes_secy2.set_ylim(-1.5, 0.9)  
        # Define custom tick positions for N2 Pressure
        axes_secy2.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])   # Adjust values based on data range
        axes_secy2.tick_params(axis='y', labelsize=7)
        

        # Add vertical lines for door_open, temp_alarm, co2_alarm, and o2_alarm event markings:
        for idx, row in self.combined_df.iterrows():
            if row[self.combined_df.columns[15]]:
                for ax in axes:
                    ax.axvline(x=row[self.combined_df.columns[0]], color='black', linestyle='-.', linewidth=0.75, ymin=0.00, ymax=0.04) # ymin and ymax values to set the height of the line
            if row[self.combined_df.columns[12]]:
                axes[0].axvline(x=row[self.combined_df.columns[0]], color='red', linestyle='dotted', linewidth=0.75, ymin=0.95, ymax=1.0)
            if row[self.combined_df.columns[13]]:
                axes[1].axvline(x=row[self.combined_df.columns[0]], color='red', linestyle='dotted', linewidth=0.75, ymin=0.95, ymax=1.0)
            if row[self.combined_df.columns[14]]:
                axes[2].axvline(x=row[self.combined_df.columns[0]], color='red', linestyle='dotted', linewidth=0.75, ymin=0.95, ymax=1.0)

        # Create custom legend entries for the vertical lines
        custom_lines = [
            Line2D([0], [0], color='black', linestyle='-.', linewidth=0.75, label='Door opening'),
            Line2D([0], [0], color='red', linestyle='dotted', linewidth=0.75, label='Sensor alarm'),
            Line2D([0], [0], color='#4a4a4a', linestyle='dashed', linewidth=0.75, label='Set point'),
            Line2D([0], [0], color='#3232a8', linestyle='solid', linewidth=0.75, label='Conc.\nTemp.'),
            Line2D([0], [0], color='#73f707', linestyle='solid', linewidth=0.75, label='Flow'),
            Line2D([0], [0], color='#eb34d8', linestyle='solid', linewidth=0.75, label='Pressure')
                   ]
        # Add the custom legend to the figure
        fig.legend(handles=custom_lines, fontsize='7', loc='upper right')

        # Adjust the spacing between subplots
        plt.tight_layout()
        
        # Set the locator
        locator = mdates.AutoDateLocator(minticks=10, maxticks=50)
        formatter = mdates.ConciseDateFormatter(locator)
        axes[2].xaxis.set_major_locator(locator)
        axes[2].xaxis.set_major_formatter(formatter)
        axes[2].set_xlabel('Date / time')

        # Customize the tick font size on the X-axis for all subplots
        for ax in axes:
            ax.tick_params(axis='x', labelsize=8)  # Change the tick font size on the X-axis


        # Display the plots
        plt.show()


def main():
    app = QApplication(sys.argv)
    font = QFont("Monaco", 8)
    app.setFont(font)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


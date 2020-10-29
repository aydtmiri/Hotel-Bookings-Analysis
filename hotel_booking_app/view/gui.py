#######################################################################
__author__ = "Miriam Aydt"
__program__ = "Create user interface of application"

#######################################################################

import csv
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import re
import hotel_booking_app.src.processing.analyse_data as analyse
import hotel_booking_app.src.preparation.prepare_data as prep
import hotel_booking_app.settings as setting
import os.path
import logging


class HotelBookingGUI:
    """
    Class that represents GUI of the hotel booking reporting application.
    """

    def __init__(self, master):
        """
        Initialize class HotelBookingGUI
        """
        self.master = master
        self.csv_path = 'No file selected'
        self.w = self.master.winfo_screenwidth()
        self.h = self.master.winfo_screenheight()
        self.lbl_header = tk.Label()
        self.lbl_description_date = tk.Label()
        self.lbl_description_csv = tk.Label()
        self.lbl_file_path = tk.Label()
        self.lbl_date = tk.Label()
        self.entry_file_path = tk.Entry()
        self.entry_date = tk.Entry()
        self.date = tk.StringVar()
        self.btn_browse = tk.Button()
        self.btn_analyse = tk.Button()
        self.table_active_bookings = tk.Frame()
        self.table_total_guests = tk.Frame()

        self.load_view()

    def load_view(self):
        """
        Load view of window.
        Basic view contains:
                    - Date input
                    - File input
        """

        # Define window
        # Including:
        #           - setting window size
        #           - setting title
        self.master.geometry("%dx%d" % (self.w, self.h))
        self.master.title('Hotel Bookings Reporting')

        # Define header of content
        self.lbl_header = tk.Label(root,
                                   text='Welcome to the Hotel Bookings '
                                        'Reporting analysis application!',
                                   font=("Calibri", 20, 'bold')) \
            .pack(side=tk.TOP, pady=10)

        # Add label for description of application
        self.lbl_description_date = tk.Label(root,
                                             text='After entering a date and '
                                                  'providing a CSV file, please'
                                                  ' click on the button'
                                                  '"Analyse Data" to start the'
                                                  ' analysis.',
                                             font=("Calibri", 12)) \
            .pack(side=tk.TOP, pady=10)

        # Define container for tables
        self.table_container = tk.Frame(root).pack(side=tk.TOP)

        # Date input
        self.lbl_date = tk.Label(root,
                                 text='Input a date (YYYY-MM-DD):',
                                 font=("Calibri", 12, 'bold')) \
            .pack(side=tk.TOP)

        self.entry_date = tk.Entry(root, textvariable=self.date) \
            .pack(side=tk.TOP)

        # Explanation for uploading csv file
        self.lbl_description_csv = tk.Label(root,
                                            text="Upload a CSV file on "
                                                 "which the analysis should be"
                                                 " performed on.",
                                            font=("Calibri", 12)) \
            .pack(side=tk.TOP, pady=10)

        # File input
        self.btn_browse = tk.Button(root,
                                    text='Browse for CSV file',
                                    command=self.import_csv_data,
                                    font=("Calibri", 12)) \
            .pack(side=tk.TOP)

        # Label for displaying path of file
        self.lbl_file_path = tk.Label(root, text='File path:',
                                      font=("Calibri", 12, 'bold')) \
            .pack(side=tk.TOP)

        self.lbl_path = tk.Label(root, text=self.csv_path,
                                 font=("Calibri", 12))

        self.lbl_path.pack(side=tk.TOP)

        # Analyse Button
        self.btn_browse = tk.Button(root,
                                    text='Analyse data',
                                    command=self.display_result_tables,
                                    font=("Calibri", 12)
                                    ) \
            .pack(side=tk.TOP, pady=10)

    def create_table(self, heading, csv_file_path, table_frame):
        """
        Create a table with generic content and columns.

        :param heading: Heading of table
        :param csv_file_path: Path to csv file containing content
        :param table_frame: Frame to which table is added to
        :return: Frame containing table
        """

        # Load csv file
        with open(csv_file_path) as csv_file:
            reader = csv.DictReader(csv_file, delimiter=',')

            # Get all column headers
            table_column_headers = reader.fieldnames

            # Define frame for table
            table_frame = tk.Frame(root, width=20)
            table_frame.pack(side=tk.TOP)

            # Define table heading
            lbl_table_heading = tk.Label(table_frame,
                                         text=heading,
                                         font=("Calibri", 12, 'bold'))

            lbl_table_heading.pack(side=tk.TOP, pady=10)

            # Define scrollbars
            scrollbar_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
            scrollbar_y = tk.Scrollbar(table_frame, orient=tk.VERTICAL)

            # Define treeview
            tree = ttk.Treeview(table_frame,
                                columns=table_column_headers,
                                height=12,
                                selectmode="none",
                                yscrollcommand=scrollbar_y.set,
                                xscrollcommand=scrollbar_x.set)
            tree['show'] = 'headings'
            scrollbar_y.config(command=tree.yview)
            scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_x.config(command=tree.xview)
            scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

            # Add column headers to treeview
            for i, column_header in enumerate(table_column_headers):
                tree.heading(column_header, text=column_header, anchor=tk.W)
                tree.column(i, stretch=tk.NO, minwidth=0, width=150)

            tree.pack()

            # For every row of csv table, add row to table
            index = 0
            for row in reader:
                row_values = []

                for column_header in table_column_headers:
                    row_values.append(row[column_header])

                tree.insert("", index, values=row_values)
                index += 1

            return table_frame

    def import_csv_data(self):
        """
        Open filesystem picker and save file path string.
        """
        self.csv_path = askopenfilename()
        self.lbl_path['text'] = self.csv_path

    def display_result_tables(self):
        """
        Display result tables of analysis.
        Containing:
                    - Evaluate user input
                    - Call logic for analysis
                    - Create tables representing results
        """
        # Evaluate user input
        output_message = self.evaluate_input()

        # Check if there are errors in user input.
        # If so, show messagebox with error message
        # else proceed with calling logic
        if output_message:
            messagebox.showwarning("Invalid User Input", output_message)
        else:

            # Reset tables
            self.reset_tableview()

            try:

                # Call logic to import csv data from path and clean it
                prep.import_clean_data(
                    self.csv_path,
                    os.path.join(setting.RAW_DATA_PATH, setting.RAW_NAME),
                    0.8)

            except Exception:
                messagebox.showwarning(
                    "Error during analysis",
                    'There has been an error during preparing the data.'
                    ' Please try again.')
                logging.error('Failed to import data: ', exc_info=True)

                return

            # Call logic to analyse active bookings
            # If successful, create corresponding table
            # If not successful, show error message and return
            try:
                analyse.analyse_active_bookings(
                    os.path.join(setting.RAW_DATA_PATH, setting.RAW_NAME),
                    os.path.join(setting.RESULT_DATA_PATH,
                                 setting.RESULT_ACTIVE_BOOKINGS),
                    self.date.get(),
                    7)

            except Exception:
                messagebox.showwarning(
                    "Error during analysis",
                    'Active bookings could not be analysed.')
                logging.error('Failed to analyse bookings: ', exc_info=True)

                return

            # Create table for active bookings
            self.table_active_bookings = self.create_table(
                setting.RESULT_ACTIVE_BOOKINGS + ": Currently active bookings",
                os.path.join(setting.RESULT_DATA_PATH,
                             setting.RESULT_ACTIVE_BOOKINGS),
                self.table_active_bookings)

            # Call logic to analyse total guest per day
            # If successful, create corresponding table
            # If not successful, show error message
            try:
                analyse.analyse_total_guests(
                    os.path.join(setting.RAW_DATA_PATH, setting.RAW_NAME),
                    os.path.join(setting.RESULT_DATA_PATH,
                                 setting.RESULT_TOTAL_GUESTS),
                    self.date.get(),
                    7)

            except Exception:
                messagebox.showwarning(
                    'Error during analysis',
                    'Total guests could not be analysed.'
                )
                logging.error('Failed to analyse total guests: ', exc_info=True)
                return

            # Create table for total guests per day
            self.table_total_guests = self.create_table(
                setting.RESULT_TOTAL_GUESTS + ': Total guests per day',
                os.path.join(setting.RESULT_DATA_PATH,
                             setting.RESULT_TOTAL_GUESTS),
                self.table_total_guests)

    def evaluate_input(self):
        """
        Evaluate user input and create error messages.
        """

        output_message = []

        # Check pattern of date using a regex expression
        pattern = \
            '^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$'
        match = re.search(pattern, self.date.get())

        if not match:
            output_message.append("Date is not valid. The format should be"
                                  " YYYY-MM-DD.\n")

        # Check if file is a csv file
        if self.csv_path and not self.csv_path.endswith('.csv'):
            output_message.append("Please provide a CSV file.\n")

        return output_message

    def reset_tableview(self):
        """
        Reset tableview when new analysis is requested.
        """

        if self.table_total_guests is not None:
            self.table_total_guests.pack_forget()

        if self.table_active_bookings is not None:
            self.table_active_bookings.pack_forget()


root = tk.Tk()
gui = HotelBookingGUI(root)

root.mainloop()

# ============================INITIALIZATION==============================
if __name__ == '__main__':
    root.mainloop()

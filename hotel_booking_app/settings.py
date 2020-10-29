###############################################################################
#          Here path variables, used within the code, are declared            #
###############################################################################
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

# Path of directory where csv files are saved to
RAW_DATA_PATH = os.path.join(ROOT_DIR, 'data/raw')
RESULT_DATA_PATH = os.path.join(ROOT_DIR, 'data/results')

# Name of processed csv files
RAW_NAME = 'hotel_data_raw.csv'
RESULT_ACTIVE_BOOKINGS = 'hotel_active_bookings.csv'
RESULT_TOTAL_GUESTS = 'hotel_total_guests.csv'


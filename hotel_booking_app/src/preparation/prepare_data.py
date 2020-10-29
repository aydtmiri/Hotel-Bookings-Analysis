#######################################################################
__author__ = "Miriam Aydt"
__program__ = "Prepare data for further analysis"
#######################################################################

import pandas as pd


def import_clean_data(csv_file_path, csv_file_save_to_path, threshold):
    """
    Import, clean and save csv file.

    :param csv_file_path: Path of csv file containing relevant data
    :param csv_file_save_to_path: Path of result csv file
    :param threshold: Decimal value, representing the maximum NaN percentage
                      of a row. If a row has more NaN values than the threshold,
                      it will be dropped.
    """

    df = pd.read_csv(csv_file_path)

    # Drop all rows, that have more than threshold*100 percent NaN values
    df = df.loc[:, df.isnull().sum() < threshold*df.shape[0]]

    df.to_csv(csv_file_save_to_path)

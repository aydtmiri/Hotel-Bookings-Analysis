#######################################################################
__author__ = "Miriam Aydt"
__program__ = "Analyse hotel bookings"

#######################################################################

import pandas as pd
import datetime as dt


def analyse_total_guests(csv_file_path, csv_file_save_to_path, selected_date,
                         time_span):
    """
    Calculate total number of adults, children, and babies expected
    to be in residence per day within a time span.

    :param csv_file_path: Path of csv file containing relevant data
    :param csv_file_save_to_path: Path of result csv file
    :param selected_date: Date in YYYY-MM-DD format
    :param time_span: Time span, in which guests should arrive (in days)
    """

    df_active_bookings = get_active_bookings(csv_file_path,
                                             selected_date,
                                             time_span)

    # Check if dataframe is empty.
    # If so, create empty result dataframe and save it to results
    #  After that, return
    if df_active_bookings.empty:
        df_empty = pd.DataFrame(
            columns=['stayed_date', 'adults',
                     'children', 'babies', 'total_guests_per_day'])
        # Save data frame to results
        df_empty.to_csv(csv_file_save_to_path, index=False)
        return

    selected_date = pd.to_datetime(selected_date)

    # Map each object into an unique integer.
    # This insures mapping the right stayed dates to the booking
    df_active_bookings['booking_id'] = \
        pd.factorize(df_active_bookings.apply(tuple, axis=1))[0] + 1

    # Get stayed dates of guests by calculating the range
    # between arrival date and leaving date
    df_stayed_dates = pd.concat([pd.Series(r.booking_id,
                                           pd.date_range(start=r.arrival_date,
                                                         end=r.leaving_date,
                                                         freq='D'))
                                 for r in
                                 df_active_bookings.itertuples()]).reset_index()

    df_stayed_dates.columns = ['stayed_date', 'booking_id']

    # Merge data frame of stayed dates
    # with relevant columns from original data frame.
    df_stayed_dates = pd.merge(df_stayed_dates, df_active_bookings[
        ['booking_id', 'adults', 'children', 'babies']],
                               on=['booking_id'])

    df_stayed_dates['children'] = df_stayed_dates['children'].astype(int)

    # Group stayed dates and sum corresponding guests fields.
    # This results in total adults, children, and babies per day
    df_total_guests = df_stayed_dates.groupby(['stayed_date'])[
        ['adults', 'children', 'babies']].sum().reset_index()

    # Sum up total adults, babies, and children to get total guests per day
    df_total_guests['total_guests_per_day'] = \
        df_total_guests['adults'] + \
        df_total_guests['babies'] + \
        df_total_guests['children']

    # Get only bookings, that are within range of selected time span
    df_total_guests = df_total_guests.loc[df_total_guests['stayed_date']
        .between(selected_date,
                 (selected_date + pd.to_timedelta(time_span, unit='days')))] \
        .reset_index(drop=True)

    # Save data frame to results
    df_total_guests.to_csv(csv_file_save_to_path, index=False)


def get_active_bookings(csv_file_path, selected_date,
                        time_span):
    """
    Analyse active bookings depending on selected date.

    :param csv_file_path: Path of csv file containing relevant data
    :param selected_date: Date (YYYY-MM-DD)
    :param time_span: Time span in which guests should arrive (in days)

    :return: pandas data frame with all active bookings

    """
    df = pd.read_csv(csv_file_path)

    selected_date = pd.to_datetime(selected_date)

    # Map month full names to month integer.
    # This is necessary in order to be able to map year,
    # month, and day to date.
    df['arrival_date_month'] = pd.to_datetime(df['arrival_date_month'],
                                              format='%B').dt.month

    # Map arrival year, month, and day to new data frame
    # This is necessary in order to be able to convert them to datetime
    df2 = df[["arrival_date_year", "arrival_date_month",
              "arrival_date_day_of_month"]].copy()
    df2.columns = ["year", "month", "day"]

    # Convert year, month, and day of arrival to date of arrival
    df['arrival_date'] = pd.to_datetime(df2)

    # Add stays to arrival date to get leaving date
    df['leaving_date'] = pd.DatetimeIndex(df['arrival_date']) \
                         + pd.to_timedelta(df['stays_in_weekend_nights'],
                                           unit='d') \
                         + pd.to_timedelta(df['stays_in_week_nights'], unit='d')

    # Get all bookings where ->
    # leaving date is not earlier than current date
    # and arrival date is not later than selected date plus time_span days
    # and the booking is not cancelled
    # This ensures, that you only get bookings that are currently active or
    # begin in the next x days (x -> time_span)
    df_active_bookings = df.loc[
        ~((df['leaving_date'] <= selected_date)
          | (df['arrival_date'] > selected_date + dt.timedelta(days=time_span)))
        & (df['is_canceled'] == 0)]

    return df_active_bookings


def analyse_active_bookings(csv_file_path, csv_file_save_to_path, selected_date,
                            time_span):
    """
    Create result table of all active bookings.
    Includes:

    - Call function to get data frame of active bookings
    - Clean data frame in order to save it as result CSV file

    :param csv_file_path: Path of csv file containing relevant data
    :param csv_file_save_to_path: Path of result csv file
    :param selected_date: Date in YYYY-MM-DD format
    :param time_span: Time span in which guests should arrive (in days)
    """

    # Get all active bookings
    df_active_bookings = get_active_bookings(csv_file_path,
                                             selected_date,
                                             time_span)

    # Prepare data frame for saving
    # Drop unnecessary analysis columns
    df_active_bookings.drop(['leaving_date', 'arrival_date'],
                            axis=1,
                            inplace=True)

    # Drop columns with unnamed in name
    df_active_bookings.drop(
        df_active_bookings.columns[df_active_bookings.columns.str
            .contains('unnamed', case=False)],
        axis=1,
        inplace=True)

    # Convert month int to month name again
    df_active_bookings['arrival_date_month'] = \
        pd.to_datetime(df_active_bookings['arrival_date_month'],
                       format='%m').dt.month_name()

    # Save dataframe to results
    df_active_bookings.to_csv(csv_file_save_to_path, index=False)

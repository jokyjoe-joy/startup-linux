from datetime import datetime
from win10toast import ToastNotifier
import pandas as pd
import logging
import ctypes

# Global settings
# This way dates will be in the same format
DATE_STYLE = "%Y-%m-%d"

# Notification settings
TOAST_TITLE = "Don't forget finance!"
TOAST_TEXT = "Today is an expected logging date for portfolio_data.xlsx, please don't forget to fill in the expected data."
TOAST_ICON_PATH = r".\modules\icons\balloontip.ico"

# Other settings
EXCEL_FILE_NAME = r'C:\Users\Gary\Desktop\FNC\portfolio_data.xlsx'

def _(DATE_STYLE=DATE_STYLE):
    toaster = ToastNotifier()
    logging.info("Starting finance notification function.")
    # Get time
    now = datetime.now()
    # Convert it to same style as in excel file.
    current_date = now.strftime(DATE_STYLE)

    logging.info("Reading excel file %s.", EXCEL_FILE_NAME)
    # Read excel file, and only the EXP. LOG DATE column.
    data = pd.read_excel(EXCEL_FILE_NAME)
    df = pd.DataFrame(data, columns= ['EXP. LOG DATE'])

    logging.info("Checking if any expected logging date is the same as today's date.")
    # Loop through each date in the column.
    for i in range(len(df)):
        # Get cell data
        row = df.loc[i, "EXP. LOG DATE"]
        # strftime throws error if NaT
        if row is pd.NaT:
            continue
        # If today is an expected log date, show notification.
        if (row.strftime(DATE_STYLE) == current_date):
            logging.info("Today is an expected logging date: showing notification.")
            toaster.show_toast(TOAST_TITLE, TOAST_TEXT, TOAST_ICON_PATH, duration=10, threaded=True)


if __name__ == '__main__':
    _()

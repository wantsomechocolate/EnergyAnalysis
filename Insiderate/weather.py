#step 1

import numpy as np, pylab as pl, pandas as pd

book_name='DataInput2013.xlsx'
num_matches=5

def datetime2date(datetime):
    return datetime.date()

## A map of all the data
wb = pd.ExcelFile(book_name)

## The weather info currently resides on the second tab.
## is it better to refer by name or by position!?
weather_interval_data_frame=wb.parse(wb.sheet_names[1])

## From the datetime in column one, make a new column with only the date portion of each date time
weather_interval_data_frame['Date']=weather_interval_data_frame[weather_interval_data_frame.columns[0]].apply(datetime2date)

## Group the data by calendar day via the groupby method. 
weather_hourly_data_grouping=weather_interval_data_frame.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
weather_hourly_data_frame=weather_hourly_data_grouping[weather_interval_data_frame.columns[1]].agg({'Mean' : np.mean})

## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



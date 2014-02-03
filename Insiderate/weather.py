#step 1

import numpy as np, pylab as pl, pandas as pd
import wam as wam

book_name='DataInput2013.xlsx'
num_matches=5

## To map a datetime column in a pandas dataframeto a date column
def datetime2date(datetime):
    return datetime.date()

def datetime2hour(datetime):
    return datetime.hour

## A map of all the data
wb = pd.ExcelFile(book_name)

## The weather info currently resides on the second tab.
## is it better to refer by name or by position!?
weather_interval_data_frame=wb.parse(wb.sheet_names[1])

## From the datetime in column one, make a new column with only the date portion of each date time
weather_interval_data_frame['Date']=weather_interval_data_frame[weather_interval_data_frame.columns[0]].apply(datetime2date)

## Group the data by calendar day via the groupby method. 
weather_daily_data_grouping=weather_interval_data_frame.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
weather_daily_data_frame=weather_daily_data_grouping[weather_interval_data_frame.columns[1]].agg({'Mean' : np.mean})

## Retrieves dates from a file, the name of which is hardcoded into the function.
exclude_days=wam.get_excluded_days()

## This takes the data frame, uses the index (dates) and the first column of data (average wetbulb temperatures here)
## and then for each number in the list finds the k nearest numbers and their corresponding index (or date)
## It adds those results to the data frame and then returns it. 
weather_daily_dataframe=wam.add_k_1d_nearest_neighbors_to_dataframe(weather_daily_data_frame, num_matches, exclude_days)


##weather_interval_data_frame['Hour']=weather_interval_data_frame[weather_interval_data_frame.columns[0]].apply(datetime2hour)



## Get quarters worth of days from the grouping?
## Group the groups by type of day?
## Group the groups by hour?







## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



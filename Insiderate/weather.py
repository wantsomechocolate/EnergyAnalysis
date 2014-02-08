#step 1

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime

book_name='DataInput2013.xlsx'
num_matches=5

print "Getting days to be excluded from calculations from file."
exclude_days=wam.get_excluded_days()


start_date_pp=datetime.datetime(2013,9,1,0,0)
end_date_pp=datetime.datetime(2013,12,31,23,45)


start_date_all=datetime.datetime(2013,1,1,0,0)
end_date_all=datetime.datetime(2013,12,31,23,45)


## A map of all the data
print "Reading in excel data."
wb = pd.ExcelFile(book_name)

## The weather info currently resides on the second tab. Is it better to refer by name or by position!?
print "Reading in data from second sheet and creating a dataframe."
weather_interval_dataframe_all=wb.parse(wb.sheet_names[1])

print "Duplicating the first column and setting as the index."
## I do operations that are easy to do on both columns and pandas indices so here I make sure to have both
weather_interval_dataframe_all=wam.duplicate_first_column_as_index(weather_interval_dataframe_all,'DateTimeStamp')

print "Preparing data from for grouping by various time based criteria"
## Preparing data from for grouping by various time based criteria
weather_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(weather_interval_dataframe_all, start_date_all, end_date_all)

## Group the data by calendar day via the groupby method.
print "Grouping the data by calandar day."
weather_daily_grouping=weather_interval_dataframe.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
print "Calculating the mean of each group for new dataframe."
weather_daily_dataframe=weather_daily_grouping[weather_interval_dataframe.columns[1]].agg({'Mean' : np.mean})

## This takes the data frame, uses the index (dates) and the first column of data (average wetbulb temperatures here)
## and then for each number in the list finds the k nearest numbers and their corresponding index (or date)
## It adds those results to the data frame and then returns it.
print "Getting k 1d nearest neighbors in the average day dataframe."
weather_daily_dataframe=wam.add_k_1d_nearest_neighbors_to_dataframe(weather_daily_dataframe, num_matches, exclude_days)

## This function takes a df of interval data (multiple readings per day)
## and slices it down to the given dates and returns a df representing a single day
## with the average weekday, average weekend, peak day, and min day
weather_average_day_profile_dataframe_pp=wam.average_daily_metrics(weather_interval_dataframe, start_date_pp, end_date_pp, 'WetBulbTemp')


##print "That's all for now, bye."
##
##from pandas import ExcelWriter
##
##out='test.xlsx'
##
##writer = ExcelWriter(out)
##
##weather_average_day_profile_dataframe_pp.to_excel(writer,'Weather Average Day')
##weather_daily_dataframe.to_excel(writer,'Weather Daily')
##
##writer.save()


##-------------- Cue Energy Analysis ----------------------

energy_interval_dataframe_all=wb.parse(wb.sheet_names[0])

column_headings=list(energy_interval_dataframe_all.columns)
dummy=column_headings.pop(0)

energy_interval_dataframe_all=wam.duplicate_first_column_as_index(energy_interval_dataframe_all,'DateTimeStamp')

energy_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(energy_interval_dataframe_all, start_date_all, end_date_all)

## The below is causing problems because I'm grouping by hour at some point when I should be grouping by 15 minute. :(
df_ave_day_dict={}
for item in column_headings:
    energy_average_day_profile_dataframe_pp=wam.average_daily_metrics(energy_interval_dataframe, start_date_pp, end_date_pp, item)
    df_ave_day_dict[item]=energy_average_day_profile_dataframe_pp

##weather_interval_dataframe_for_dates=weather_interval_data_frame[datetime.datetime(2013,7,1,0,0):datetime.datetime(2013,7,,31,23,45)]
##weather_average_day_profile=weather_interval_data_frame.groupby(['DayType', 'Hour'], sort=False, as_index=False).apply(lambda x: list(x['WetBulbTemp']))


## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



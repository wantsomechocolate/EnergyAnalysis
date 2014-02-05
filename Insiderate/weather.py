#step 1

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime

book_name='DataInput2013.xlsx'
num_matches=5

## To map a datetime column in a pandas dataframeto a date column
def datetime2date(datetime):
    return datetime.date()

def datetime2hour(datetime):
    return datetime.hour

#should this exclude holidays?
#Yes
def datetime2bday(datetime):

####    exclude_days=wam.get_excluded_days()
####
####    date=datetime.date()
####    if date in exclude_days:
####        return 'Weekend'
####    else:
####        pass

    day_of_week=datetime.isoweekday()
    if day_of_week<=5:
        return 'Weekday'
    else:
        return 'Weekend'


start_date_pp=datetime.datetime(2013,9,1,0,0)
end_date_pp=datetime.datetime(2013,12,31,23,45)


start_date_all=datetime.datetime(2013,1,1,0,0)
end_date_all=datetime.datetime(2013,12,31,23,45)



## A map of all the data
print "read in excel data"
wb = pd.ExcelFile(book_name)

## The weather info currently resides on the second tab.
## is it better to refer by name or by position!?
print "read in weather sheet"
weather_interval_dataframe=wb.parse(wb.sheet_names[1])

## Set the date columns as the index - might have to hold off on this one, can't figure out
## how to get it to work with rest of code.
print "set first column of dataframe as the index of the dataframe"
weather_interval_dataframe=weather_interval_dataframe.set_index(weather_interval_dataframe.columns[0])

## Make the index back into a column so you have both to work with
print "Put the column that you just made the index back in as a column again"
weather_interval_dataframe.insert(0,'DateTimeStamp',weather_interval_dataframe.index)

## Get slice that will be used for band analysis
print "get slice for band analysis"
weather_interval_dataframe=weather_interval_dataframe[start_date_all:end_date_all]



## From the datetime in column one, make a new column with only the date portion of each date time, for grouping
print "Add Date column"
weather_interval_dataframe['Date']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2date)
## Add hour column
print "Add Hour column"
weather_interval_dataframe['Hour']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2hour)
## Add a daytype that seperates days into Weekday and Holiday/Weekend
print "Add daytype column"
weather_interval_dataframe['DayType']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2bday)



## Group the data by calendar day via the groupby method.
print "group by date"
weather_daily_grouping=weather_interval_dataframe.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
print "Take groups and get mean for each group"
weather_daily_dataframe=weather_daily_grouping[weather_interval_dataframe.columns[1]].agg({'Mean' : np.mean})

## Retrieves dates from a file, the name of which is hardcoded into the function.
## Maybe just roll this function into the one below
print "Get excluded holidays from file"
exclude_days=wam.get_excluded_days()

## This takes the data frame, uses the index (dates) and the first column of data (average wetbulb temperatures here)
## and then for each number in the list finds the k nearest numbers and their corresponding index (or date)
## It adds those results to the data frame and then returns it.
print "Get k 1d nearest neighbors"
weather_daily_dataframe=wam.add_k_1d_nearest_neighbors_to_dataframe(weather_daily_dataframe, num_matches, exclude_days)


## Now I'm interested only in performance period
print "Getting performance period"
weather_interval_dataframe_pp=weather_interval_dataframe[start_date_pp:end_date_pp]

## Other groupings
##weather_daily_data_grouping=weather_interval_data_frame.groupby('DayType')

#weather_average_day_profile=weather_interval_data_frame.groupby(['DayType', 'Hour'], sort=False, as_index=False).apply(lambda x: list(x['WetBulbTemp']))

## In one swoop, group by daytype and hour, get the averages for each group, then put back into df
print "group by day type and hour get mean, put back in df"
weather_average_day_profile_dataframe_pp=weather_interval_dataframe_pp.groupby(['DayType', 'Hour'], sort=False, as_index=False).agg({'WetBulbTemp':np.mean})

## Now group based on the new df
print "group the new df on daytype"
weather_average_day_profile_groups_pp=weather_average_day_profile_dataframe_pp.groupby('DayType')

## I know there will be two groups because of what the datetime to business day function does.
print "put each group in new df"
weather_average_wetbulb_weekday_pp=weather_average_day_profile_groups_pp.get_group('Weekday')['WetBulbTemp']
weather_average_wetbulb_weekend_pp=weather_average_day_profile_groups_pp.get_group('Weekend')['WetBulbTemp']

print "merge restuls into single df"
weather_average_day_profile_dataframe_pp=pd.DataFrame({'Weekday':weather_average_wetbulb_weekday_pp.values,'Weekend':weather_average_wetbulb_weekend_pp.values})
## Get quarters worth of days from the grouping?
## Group the groups by type of day?
## Group the groups by hour?


##weather_interval_dataframe_for_dates=weather_interval_data_frame[datetime.datetime(2013,7,1,0,0):datetime.datetime(2013,7,,31,23,45)]




## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



#step 1

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime

book_name='DataInput2013.xlsx'
num_matches=5

print "Getting days to be excluded from calculations from file."
## Global 
exclude_days=wam.get_excluded_days()


## To map a datetime column in a pandas dataframeto a date column
def datetime2date(datetime):
    return datetime.date()

def datetime2hour(datetime):
    return datetime.hour

def datetime2bday(datetime):

    date=datetime.date()
    if date in exclude_days: ## Exclude days is a global variable
        return 'Weekend'
    else:
        pass

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
print "Reading in excel data."
wb = pd.ExcelFile(book_name)

## The weather info currently resides on the second tab.
## is it better to refer by name or by position!?
print "Reading in data from second sheet and creating a dataframe."
weather_interval_dataframe=wb.parse(wb.sheet_names[1])



#### Set the date columns as the index - might have to hold off on this one, can't figure out
#### how to get it to work with rest of code.
##print "Setting the first column of the dataframe as the index of the dataframe."
##weather_interval_dataframe=weather_interval_dataframe.set_index(weather_interval_dataframe.columns[0])
##
#### Make the index back into a column so you have both to work with
##print "Creating a column based on the index, now both column and index operations can be performed."
##weather_interval_dataframe.insert(0,'DateTimeStamp',weather_interval_dataframe.index)

weather_interval_dataframe=wam.duplicate_first_column_as_index(weather_interval_dataframe,'DateTimeStamp')


## Get slice that will be used for band analysis
print "Getting a subset of the data for use in creating the performance band."
weather_interval_dataframe=weather_interval_dataframe[start_date_all:end_date_all]

## From the datetime in column one, make a new column with only the date portion of each date time, for grouping
print "Adding a 'Date' column from the DateTimeStamp."
weather_interval_dataframe['Date']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2date)
## Add hour column
print "Adding an 'Hour' column from the DateTimeStamp."
weather_interval_dataframe['Hour']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2hour)
## Add a daytype that seperates days into Weekday and Holiday/Weekend
print "Adding a 'DayType' column from the DateTimeStamp counting excluded days as Weekends"
weather_interval_dataframe['DayType']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2bday)

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

## Now I'm interested only in performance period
print "Getting the performance period"
weather_interval_dataframe_pp=weather_interval_dataframe[start_date_pp:end_date_pp]

## In one swoop, group by daytype and hour, get the averages for each group, then put back into df
print "Grouping by DayType and Hour, getting mean, put back in df."
weather_average_day_profile_dataframe_pp=weather_interval_dataframe_pp.groupby(['DayType', 'Hour'], sort=False, as_index=False).agg({'WetBulbTemp':np.mean})

## Now group based on the new df
print "Group the new dataframe on daytype and seperating groups to be different columns in another dataframe."
weather_average_day_profile_groups_pp=weather_average_day_profile_dataframe_pp.groupby('DayType')

## I know there will be two groups because of what the datetime to business day function does.
print "Putting each group into a new dataframe"
weather_average_wetbulb_weekday_pp=weather_average_day_profile_groups_pp.get_group('Weekday')['WetBulbTemp']
weather_average_wetbulb_weekend_pp=weather_average_day_profile_groups_pp.get_group('Weekend')['WetBulbTemp']

print "Merging results into a single dataframe."
weather_average_day_profile_dataframe_pp=pd.DataFrame({'Weekday':weather_average_wetbulb_weekday_pp.values,'Weekend':weather_average_wetbulb_weekend_pp.values})

print "Getting day with peak temp and day with lowest temp and adding to average day dataframe."
## Take the right interval df (performance period and get timestamps for max and min
weather_max_timestamp=weather_interval_dataframe_pp[weather_interval_dataframe_pp.columns[1]].idxmax()
weather_min_timestamp=weather_interval_dataframe_pp[weather_interval_dataframe_pp.columns[1]].idxmin()

weather_max_day=weather_max_timestamp.date()
weather_max_day_interval_data=weather_daily_grouping.get_group(weather_max_day)
weather_average_day_profile_dataframe_pp[str(weather_max_timestamp)]=weather_max_day_interval_data[weather_max_day_interval_data.columns[1]].values

weather_min_day=weather_min_timestamp.date()
weather_min_day_interval_data=weather_daily_grouping.get_group(weather_min_day)
weather_average_day_profile_dataframe_pp[str(weather_min_timestamp)]=weather_min_day_interval_data[weather_min_day_interval_data.columns[1]].values

print "That's all for now, bye."


## How many final products do I have?
##Interval
##Monthly?
##Daily
##Average Daily





##weather_interval_dataframe_for_dates=weather_interval_data_frame[datetime.datetime(2013,7,1,0,0):datetime.datetime(2013,7,,31,23,45)]
##weather_average_day_profile=weather_interval_data_frame.groupby(['DayType', 'Hour'], sort=False, as_index=False).apply(lambda x: list(x['WetBulbTemp']))


## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



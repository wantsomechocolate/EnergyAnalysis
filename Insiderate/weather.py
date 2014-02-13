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
print "Reading in energy data"
energy_interval_dataframe_all=wb.parse(wb.sheet_names[0])

print "Getting the number of data columns"
num_data_cols=len(energy_interval_dataframe_all.columns)-1

print "Get list of data streams"
column_headings=list(energy_interval_dataframe_all.columns)
dummy=column_headings.pop(0)

print "Make timestamp index and first column"
energy_interval_dataframe_all=wam.duplicate_first_column_as_index(energy_interval_dataframe_all,'DateTimeStamp')

print "Prepare dataframe for grouping by time"
energy_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(energy_interval_dataframe_all, start_date_all, end_date_all)

print "Getting average day profile metrics"
##df_ave_day_dict={}
##for item in column_headings:
##    energy_average_day_profile_dataframe_pp=wam.average_daily_metrics(energy_interval_dataframe, start_date_pp, end_date_pp, item)
##    df_ave_day_dict[item]=energy_average_day_profile_dataframe_pp

## Getting this right involves making the column names unique for each set. Should be easy
## Just use the first couple chars of item as column heading. 
df_ave_day_list=[]
for item in column_headings:
    energy_average_day_profile_dataframe_pp=wam.average_daily_metrics(energy_interval_dataframe, start_date_pp, end_date_pp, item)
    df_ave_day_list.append(energy_average_day_profile_dataframe_pp)

if len(df_ave_day_list)==1:
    ave_day_stats_pp=df_ave_day_list[0]
else:  
    ave_day_stats_pp=df_ave_day_list[0].join(df_ave_day_list[1:], how='outer')





##------------------------ Join my Band --------------------------------

print "Grouping interval energy data by date"
energy_interval_groups_by_date=energy_interval_dataframe.groupby('Date')

## Stats are the band, data are the numbers used to calculate the stats
energy_interval_band_stats_df_list=[]
energy_interval_band_data_df_list=[]

## for loop starting at index 1 instead of 0
for data_col in range(1,num_data_cols+1):

    ## Make and empty structure to store interval data by day to then later concatonate it all together
    list_of_list_of_series=[]
    for i in range(num_matches):
        list_of_list_of_series.append([])


    band_info_df=pd.DataFrame()

    ## num_matches is determined way in the beginning, it's the number of similar days
    for col in range(1,num_matches+1):
        ## Get a column out of the weather daily data frame
        current_col=weather_daily_dataframe[weather_daily_dataframe.columns[col]]
        ## for all the dates in the current column
        for item in current_col:
            ## Go to the interval data grouped by date and use the date as the index to get the data. 
            current_group=energy_interval_groups_by_date.get_group(item)
            ## Get only the data you want from the grouping (depends on data_col)
            current_series=current_group[current_group.columns[data_col]]
            ## Add that series to the list of lists!
            list_of_list_of_series[col-1].append(current_series)

    ## This iterates through the list of lists and uses concat to combine all the series in a
    ## given list.
    energy_interval_band_data_df=pd.DataFrame()
    for i in range(len(list_of_list_of_series)):
        current_col=pd.concat(list_of_list_of_series[i])
        energy_interval_band_data_df['Day '+str(i+1)]=current_col.values

    ## Because the analysis was sort of taken out of dataframe lane, the index went missing
    ## Add it back in here
    energy_interval_band_data_df=energy_interval_band_data_df.set_index(energy_interval_dataframe[energy_interval_dataframe.columns[0]])



    ## Copy the data frame that consists of the datetime index and the energy data for the similar days
    energy_interval_band_stats_df=energy_interval_band_data_df.copy(deep=True)



    ## Add the band data to a list, this will be joined by other lists of there is more than one data stream
    ## I.E elec and steam. I might make this a dictionary at some point and
    ## print this dfs to their own sheets because they won't be used in any formulas in the supplemental
    ## spreadsheet but they would be useful to look at. 
    energy_interval_band_data_df_list.append(energy_interval_band_data_df)

    ## Get a shortened data heading, This could cause problems if two datasreams
    ## have the same first four letters in there column heading
    data_heading=str(energy_interval_dataframe.columns[data_col][:4])


    energy_interval_band_stats_df[data_heading]=energy_interval_dataframe[energy_interval_dataframe.columns[data_col]].values
    mean=energy_interval_band_stats_df.mean(1)
    standard_dev=energy_interval_band_stats_df.std(1)
    
    energy_interval_band_stats_df[data_heading+'-Mean']=mean
    energy_interval_band_stats_df[data_heading+'-StDev']=standard_dev


    energy_interval_band_stats_df=energy_interval_band_stats_df.ix[:,num_matches:]

    energy_interval_band_stats_df[data_heading+'-Upper']=energy_interval_band_stats_df[energy_interval_band_stats_df.columns[1]]+energy_interval_band_stats_df[energy_interval_band_stats_df.columns[2]]
    energy_interval_band_stats_df[data_heading+'-Lower']=energy_interval_band_stats_df[energy_interval_band_stats_df.columns[1]]-energy_interval_band_stats_df[energy_interval_band_stats_df.columns[2]]

    energy_interval_band_stats_df_list.append(energy_interval_band_stats_df)


if len(energy_interval_band_stats_df_list)==1:
    energy_interval_band_stats_df_all=energy_interval_band_stats_df_list[0]
else:  
    energy_interval_band_stats_df_all=energy_interval_band_stats_df_list[0].join(energy_interval_band_stats_df_list[1:], how='outer')



#energy_band_stats_by_day_df=
energy_interval_band_stats_df_all=df
df.insert(0,'DateTimeStamp',df.index)
df['Date']=df[df.columns[0]].apply(wam.datetime2date)
## This automatically ignores the non number columns!
energy_band_stats_by_day_df=df.groupby('Date').agg(np.sum)

## Do the same thing for months
## Do the same thing for weeks? Make a custom function that looks and the modulus of how many days you are
## away from the first day? start at zero and then remove that group later?



## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 



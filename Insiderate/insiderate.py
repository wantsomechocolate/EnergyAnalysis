import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime, time, os
from marbles import glass as chan

time_list=[]
time_list.append(time.time())

divider="\n---------------------------------------------------------------------------\n"
print divider,"-------------------Welcome to Insiderate (In-sid-er-ate)-------------------",divider

## Have user navigate to desired book and show them what they chose.
print "--Please navigate to the .xlsx file containing your data\n"
book_name=chan.getPath(os.getcwd())  #,ext_list=['.xlsx'])
print "--You chose to analyze   :"+book_name

## Get output book name by adding results and a time stamp to the filename
output_bookname=chan.add_to_filename(book_name,"-Results-"+str(int(time_list[0])))
output_book = pd.ExcelWriter(output_bookname)
print "--Output to be saved here:"+output_bookname+"."


## How many similar days do you want to return?
print divider+"\n--Now you have to tell me how many days to be used when calculating the band. \
For 1 year, put 3, for 1.5 years, put 4, for 2 or more years, put 5. 6 is max\n"
default_choice=5
num_matches=chan.getIntegerInput(3,6,"--Just press enter to use the number brackets ["+str(default_choice)+"]> ",default_choice,[])

## The days to exclude are in a seperate text file
print divider
print "Getting list of holidays from text file to exclude them from analysis"
exclude_days=wam.get_excluded_days()

print divider

## Get the date range for the performance period (quarter or month usually)
## In the future this function will check to make sure that the dates given are within the bounds of the data given
## For both weather and energy usage.
## These date ranges should be DATES not DATETIMES
print "Enter the start and end date for the performance period (The quarter or month usually)."
performance_period=wam.get_date_range_from_user()
start_date_pp=performance_period[0]
end_date_pp=performance_period[1]

print divider

## Date range for the data to be analysed for band reasons. If you give 2.5 years of data, but want to analyze
## only two years, say so here! I should give choice to "Use entire data set"
print "Enter the date range for the analysis period. Should hopefully be at least a year, Preferably two"
analysis_period=wam.get_date_range_from_user()
start_date_all=analysis_period[0]
end_date_all=analysis_period[1]

print divider

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


## Write to excel
weather_average_day_profile_dataframe_pp.to_excel(output_book,"WBTAveDay")



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


ave_day_stats_pp.to_excel(output_book,"EnergyAveDay")


##------------------------ Join my Band --------------------------------

print "Grouping interval energy data by date"
energy_interval_groups_by_date=energy_interval_dataframe.groupby('Date')

## Stats are the band, data are the numbers used to calculate the stats
energy_interval_band_stats_df_list=[]
energy_interval_band_data_df_list=[]
energy_band_stats_by_day_df_list=[]

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

    ## Because the analysis was sort of taken out of dataframe land, the index went missing
    ## Add it back in here
    energy_interval_band_data_df=energy_interval_band_data_df.set_index(energy_interval_dataframe[energy_interval_dataframe.columns[0]])



    



    ## Copy the data frame that consists of the datetime index and the energy data for the similar days
    energy_interval_band_stats_df=energy_interval_band_data_df.copy(deep=True)

    ## Add the band data to a list, this will be joined by other lists if there is more than one data stream
    ## I.E elec and steam. I might make this a dictionary at some point and
    ## print this dfs to their own sheets because they won't be used in any formulas in the supplemental
    ## spreadsheet but they would be useful to look at. 
    energy_interval_band_data_df_list.append(energy_interval_band_data_df)

    ## Get a shortened data heading, This could cause problems if two datasreams
    ## have the same first four letters in there column heading
    data_heading=str(energy_interval_dataframe.columns[data_col][:4])


    ## I wanted to print this data but maybe later
    #energy_interval_band_data_df.to_excel(output_book,data_heading+"-SimDayData")


    ## Get the mean of all values in either the stats df or the band df they are the same right now
    mean=energy_interval_band_stats_df.mean(1)
    standard_dev=energy_interval_band_stats_df.std(1)
    variance=standard_dev**2

    ## Add data the actual interval data to the stats df
    energy_interval_band_stats_df[data_heading]=energy_interval_dataframe[energy_interval_dataframe.columns[data_col]].values

    ## Add the three metrics you just got
    energy_interval_band_stats_df[data_heading+'-Mean']=mean
    energy_interval_band_stats_df[data_heading+'-StDev']=standard_dev
    energy_interval_band_stats_df[data_heading+'-Var']=variance

    ## Reset the stats df so that it does not include the band data, that is already stored elsewhere.
    energy_interval_band_stats_df=energy_interval_band_stats_df.ix[:,num_matches:]




## Above got the stats base on 15 minute data, below is to get the stats by day
    
    ## Make another copy of band stats?
    df=energy_interval_band_stats_df.copy(deep=True)
    ## Insert the index of the copy as the first column
    df.insert(0,'DateTimeStamp',df.index)
    ## Add  a column for the date
    df['Date']=df[df.columns[0]].apply(wam.datetime2date)
    ## Group by that column and then aggregate the groups by summation. 
    energy_band_stats_by_day_df=df.groupby('Date').agg(np.sum)


    

    ## This takes the sum of the variances and square roots it, which gives us the aggregate standard deviation
    energy_band_stats_by_day_df[data_heading+'-VarRoot']=energy_band_stats_by_day_df[energy_band_stats_by_day_df.columns[-1]].apply(np.sqrt)

    ## Take the var root and add to mean for upper
    energy_band_stats_by_day_df[data_heading+'-Upper']=energy_band_stats_by_day_df[energy_band_stats_by_day_df.columns[1]]+energy_band_stats_by_day_df[energy_band_stats_by_day_df.columns[4]]

    ## Subtract from mean for lower
    energy_band_stats_by_day_df[data_heading+'-Lower']=energy_band_stats_by_day_df[energy_band_stats_by_day_df.columns[1]]-energy_band_stats_by_day_df[energy_band_stats_by_day_df.columns[4]]
    
    ## Do the same thing for the interval data (but just use the standarad deviation
    energy_interval_band_stats_df[data_heading+'-Upper']=energy_interval_band_stats_df[energy_interval_band_stats_df.columns[1]]+energy_interval_band_stats_df[energy_interval_band_stats_df.columns[2]]
    energy_interval_band_stats_df[data_heading+'-Lower']=energy_interval_band_stats_df[energy_interval_band_stats_df.columns[1]]-energy_interval_band_stats_df[energy_interval_band_stats_df.columns[2]]

    ## Add the interval df to the list to be concatonated later
    energy_interval_band_stats_df_list.append(energy_interval_band_stats_df)

    ## Add the daily df to the list to be concatonated later
    energy_band_stats_by_day_df_list.append(energy_band_stats_by_day_df)

## the stats list has one item your are done
if len(energy_interval_band_stats_df_list)==1:
    energy_interval_band_stats_df_all=energy_interval_band_stats_df_list[0]
else:  
    energy_interval_band_stats_df_all=energy_interval_band_stats_df_list[0].join(energy_interval_band_stats_df_list[1:], how='outer')


## If they have more than one item then use join and the 'outer' argument for the how parameter to join them by column into one big df
if len(energy_band_stats_by_day_df_list)==1:
    energy_band_stats_by_day_df_all=energy_band_stats_by_day_df[0]
else:  
    energy_band_stats_by_day_df_all=energy_band_stats_by_day_df_list[0].join(energy_band_stats_by_day_df_list[1:], how='outer')


energy_band_stats_by_day_df_all.to_excel(output_book,"BandData")





#------------------------------------------------------------------------
start_time_for_plotting_average_day=datetime.datetime(2000,1,1,0,0)
time_range_for_plotting_average_day=[]
for i in range(96):
    time_range_for_plotting_average_day.append(start_time_for_plotting_average_day+datetime.timedelta(minutes=15*i))
#------------------------------------------------------------------------


## Bucket analysis

bucketed_usage_all_streams=[]

for data_col in range(1,num_data_cols+1):

    zero_index=data_col-1

## 1.) Find date range for most recent year and take slice from main thing.

## Organize the interval data into a list of lists. Days of hours.

    print "Showing the average weekday, weekend and day with peak for "+ str(column_headings[zero_index])+"."
    ave_day_plot=pl.plot_date(time_range_for_plotting_average_day,df_ave_day_list[zero_index][df_ave_day_list[zero_index].columns[0]],'g-')
    ave_day_plot=pl.plot_date(time_range_for_plotting_average_day,df_ave_day_list[zero_index][df_ave_day_list[zero_index].columns[1]],'b-')
    ave_day_plot=pl.plot_date(time_range_for_plotting_average_day,df_ave_day_list[zero_index][df_ave_day_list[zero_index].columns[2]],'r-')
    pl.show()

    
    new_df=pd.DataFrame()
    new_df['Date']=energy_interval_dataframe['Date']
    new_df[energy_interval_dataframe.columns[data_col]]=energy_interval_dataframe[energy_interval_dataframe.columns[data_col]]
    groups=new_df.groupby('Date')
    new_list=list(groups)
    int_data_by_day=[]
    for i in range(len(groups)):
        int_data_by_day.append(list(new_list[i][1][energy_interval_dataframe.columns[data_col]]))


    date_list=list(energy_interval_dataframe.groupby('Date').agg(np.sum).index)

    end_date_bucket=end_date_pp

    bucket_date_range=wam.get_bucket_date_range_from_user(end_date=end_date_bucket)


    try:
        start_date_index=date_list.index(bucket_date_range[0])
    except ValueError:
        start_date_index=0

    try:
        end_date_index=date_list.index(bucket_date_range[1])
    except:
        end_date_index=-1
        print "--Something went wrong getting the end date"
        print "--Defaulting to the last date in list"



    ## Instead of the open closed bs, as "What time does the building go from closed to open?"
    ## and "What time does the building go from open to closed?"
    bucket_open_closed_hours=wam.get_operating_hours_from_user(debug=False)

    ## This makes matrix of the right size with the state of open or closed for each hour EACH DAY, in case we ever want to have them change
    bucket_operating_hours_by_day=[]
    for i in range((bucket_date_range[1]-bucket_date_range[0]).days):
        bucket_operating_hours_by_day.append(bucket_open_closed_hours)

    bucketed_usage=wam.get_bucketed_usage(bucket_operating_hours_by_day, date_list, start_date_index, end_date_index, int_data_by_day)

    bucketed_usage_all_streams.append(bucketed_usage)


bucketed_usage_df=pd.DataFrame()
bucketed_usage_df['Date']=bucketed_usage_all_streams[0][2]

for i in range(len(bucketed_usage_all_streams)):
    bucketed_usage_df[energy_interval_dataframe.columns[i+1][:4]+'-Occ']=bucketed_usage_all_streams[i][0]
    bucketed_usage_df[energy_interval_dataframe.columns[i+1][:4]+'-Unocc']=bucketed_usage_all_streams[i][1]

bucketed_usage_df=bucketed_usage_df.set_index('Date')


bucketed_usage_df.to_excel(output_book,"Bucketed Usage")



    


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


output_book.save()

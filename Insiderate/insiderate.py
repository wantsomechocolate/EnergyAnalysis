

##############################---------------Imports-------------------#######################

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime, time, os
from marbles import glass as chan

from openpyxl import Workbook, load_workbook
from openpyxl.style import Color, Fill
from openpyxl.cell import Cell



## This allows the program to run completely without user input, or not. 
debug=True

## This is for cosmetic stuff
divider="\n---------------------------------------------------------------------------\n"


## Keep track of the time it takes to do various things
time_list=[]
time_list.append(time.time())


print divider,"-------------------Welcome to Insiderate (In-sid-er-ate)-------------------",divider



##############################---------------File Logistics-------------------#######################


## Have user navigate to desired book and show them what they chose.
if debug==False:
    print "--Please navigate to the .xlsx file containing your data\n"
    book_name=chan.getPath(os.getcwd())
    print "--You chose to analyze: "+book_name+'\n'
else:
    print "--Please navigate to the .xlsx file containing your data\n"
    book_name='/home/wantsomechocolate/Code/EnergyAnalysis/ZY-IO/Working Input/Three Years/TwoColumnInput.xlsx'
    print "--You chose to analyze: "+book_name+'\n'


## Get output book name by adding "results" and a time stamp to the filename
## 'add_to_filename' adds text to file name without affecting the extension

output_bookname=chan.add_to_filename(book_name,"-Results-"+str(int(time_list[0])))
output_book = pd.ExcelWriter(output_bookname)

output_calendar_name=chan.add_to_filename(book_name,"-Calendars-"+str(int(time_list[0])))


print "--Output filepath   : "+output_bookname+'\n'


## How many similar days do you want to return?
print divider+"\n--Now you have to tell me how many days to be used when calculating the band"+'\n'
print "----For 1 year, put 3, for 1.5 years, put 4, for 2 or more years, put 5. 6 is max"+'\n'
default_choice=5

if debug==False:
    num_matches=chan.getIntegerInput(3,6,"----Just press enter to use the number brackets ["+str(default_choice)+"]> ",default_choice,[])

else:
    num_matches=default_choice

print ""

##############################---------------Retrieve holiday data-------------------#######################

## The days to exclude are in a seperate text file
print "--Getting list of holidays from text file to exclude them from analysis"+divider
exclude_days=wam.get_excluded_days()




##############################---------------Retrieve weather data-------------------#######################

## This spreadsheet is shipped with the program and can be updated and maintaned seperate from the energy usage data
weather_book_name='program_data/WeatherData.xlsx'


## Get the weather data
print "--Reading in weather data"+'\n'
wbw = pd.ExcelFile(weather_book_name)


## Weather only has one tab right now that is referred to using the 0 index
weather_interval_dataframe_all=wbw.parse(wbw.sheet_names[0])


print "--Duplicating the first column and setting as the index."+'\n'
## I do operations that are easy to do on both columns and pandas indices so here I make sure to have both
weather_interval_dataframe_all=wam.duplicate_first_column_as_index(weather_interval_dataframe_all,'DateTimeStamp')


##############################---------------Retrieve energy data-------------------#######################


wb = pd.ExcelFile(book_name)


print "--Reading in energy data"+'\n'
energy_interval_dataframe_all=wb.parse(wb.sheet_names[0])


print "--Getting the number of data columns"+'\n'
num_data_cols=len(energy_interval_dataframe_all.columns)-1


print "--Get list of data streams"+'\n'
column_headings=list(energy_interval_dataframe_all.columns)
dummy=column_headings.pop(0)


print "--Make timestamp index and first column"+'\n'
energy_interval_dataframe_all=wam.duplicate_first_column_as_index(energy_interval_dataframe_all,'DateTimeStamp')



### THIS STEP IS HUGE, I'm filling in the missing data up to four gaps accross. For example,
# a gap of ten will turn into a gap of 6.
#energy_interval_dataframe_all=energy_interval_dataframe_all.interpolate(limit=4)




##############################-------------Converge on working set of dates----------------#######################

## filling in missing data
## This uses a linear fill, and limits the fill to an hour past the start of the missing data. Unfortunately it does not
## abort the fill if the na gap is longer than 1 hour, which is what I actually want.
## Give the gap breakdown to the user and let them decide. 
##newdf.interpolate(limit=4)
##list of vars
##exclude_days
##weather_interval_dataframe_all
##energy_interval_dataframe_all

########start_date_list=[]
########end_date_list=[]
########
########exclude_days_start=min(exclude_days)
########exclude_days_end=max(exclude_days)
########exclude_days_elap=exclude_days_end-exclude_days_start
########exclude_years_elap=round(exclude_days_elap.days/365.0,2)
########
########print "--The excluded days go from "+str(exclude_days_start)+" to "+str(exclude_days_end)+" and span about "+str(exclude_years_elap)+" years."+"\n"
########
########## Get first and last timestamp of raw weather data set
########weather_raw_data_start=min(weather_interval_dataframe_all.index)
########weather_raw_data_end=max(weather_interval_dataframe_all.index)
########
########start_date_list.append(weather_raw_data_start)
########end_date_list.append(weather_raw_data_end)
########
########weather_raw_data_days_elap=weather_raw_data_end-weather_raw_data_start
########weather_raw_data_years_elap=round(weather_raw_data_days_elap.days/365.0,2)
########
########print "--The weather data goes from "+str(weather_raw_data_start)+" to "+str(weather_raw_data_end)+" and spans about "+str(weather_raw_data_years_elap)+" years."+"\n"
########
########
########
########## Get first and last timestamp of raw energy data set
########energy_raw_data_start=min(energy_interval_dataframe_all.index)
########energy_raw_data_end=max(energy_interval_dataframe_all.index)
########
########start_date_list.append(energy_raw_data_start)
########end_date_list.append(energy_raw_data_end)
########
########energy_raw_data_days_elap=energy_raw_data_end-energy_raw_data_start
########energy_raw_data_years_elap=round(energy_raw_data_days_elap.days/365.0,2)
########
########print "--The energy data goes from "+str(energy_raw_data_start)+" to "+str(energy_raw_data_end)+" and spans about "+str(energy_raw_data_years_elap)+" years."+"\n"
########
########
########lower_bound_date=max(start_date_list)
########lower_bound_index=start_date_list.index(lower_bound_date)
########upper_bound_date=min(end_date_list)
########upper_bound_index=end_date_list.index(upper_bound_date)
########
########if lower_bound_index==0:
########    print "--The oldest date you can use is "+str(lower_bound_date)+" because you don't have enough weather data to go back farther."+"\n"
########else:
########    print "--The oldest date you can use is "+str(lower_bound_date)+" because you don't have enough energy data to go back farther."+"\n"
########
########
########if upper_bound_index==0:
########    print "--The newest date you can use is "+str(upper_bound_date)+" because you don't have enough weather data to go forward."+"\n"
########else:
########    print "--The newest date you can use is "+str(upper_bound_date)+" because you don't have enough energy data to go forward."+"\n"
########    #print "--If you want, I can change the upper bound date to be that of the weather, would you like to do that?"
########
########if exclude_days_start<=lower_bound_date.date():
########    print "--The exlcuded days go back far enough to cover the lower bound date"+"\n"
########else:
########    print "--The exlcuded days do not go back far enough to cover the lower bound date, which is "+str(lower_bound_date)+"."+"\n"
########    print "--You can go add days to the list and rerun, you can ignore this warning, or I can change the lower_bound_date"+"\n"
########
########if exclude_days_end>=upper_bound_date.date():
########    print "--The excluded days go far enough to cover the upper bound date"+"\n"
########else:
########    print "--The excluded days do not go far enough to cover the upper bound date, which is "+str(upper_bound_date)+"."+"\n"
########    print "--I highly recommend going to the holiday list and adding holidays. You can ignore this error (don't do that)"+"\n"
########    print "--Or I can change the upper bound date to match the upper bound date of the excluded holidays."+"\n"

lower_bound_date, upper_bound_date = wam.get_lower_and_upper_bound_dates(exclude_days, weather_interval_dataframe_all, energy_interval_dataframe_all)

## Performance period date range
print "--Enter the START DATE and END DATE for the performance period (Usually 1-3 months)"+'\n'

if debug==False:
    start_date_pp, end_date_pp = wam.get_date_range_from_user(lower_bound_date.date(), upper_bound_date.date())
else:
    start_date_pp,end_date_pp=[datetime.date(2013,6,1), datetime.date(2013,8,31)]



## Analysis period date range(1-2 years usually)
print "--Enter the date range for the analysis period. Should hopefully be at least a year, Preferably two"+'\n'

if debug==False:
    start_date_all, end_date_all=wam.get_date_range_from_user(lower_bound_date.date(), upper_bound_date.date())
else:
    start_date_all, end_date_all=[datetime.date(2011,9,1), datetime.date(2013,8,31)]



print ""







## At this point the user should have their desired dates being analyzed and they should work with the data chosen.
## other wise you have failed. 

###----------------------------------------The rest--------------------------------------------------------



print "--Preparing data from for grouping by various time based criteria"+'\n'
## Preparing data from for grouping by various time based criteria


#####################################################################
## Do something more intelligent than fail when there is not enough data in the weather spreadsheet to properly analyze the
## desired date range!!!!!
weather_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(weather_interval_dataframe_all, start_date_all, end_date_all)
#####################################################################


## Group the data by calendar day via the groupby method.
print "--Grouping the data by calandar day."+'\n'
weather_daily_grouping=weather_interval_dataframe.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
print "--Calculating the mean of each group for new dataframe."+'\n'
weather_daily_dataframe=weather_daily_grouping[weather_interval_dataframe.columns[1]].agg({'Mean' : np.mean})

## This takes the data frame, uses the index (dates) and the first column of data (average wetbulb temperatures here)
## and then for each number in the list finds the k nearest numbers and their corresponding index (or date)
## It adds those results to the data frame and then returns it.
print "--Getting k 1d nearest neighbors in the average day dataframe."+'\n'
weather_daily_dataframe=wam.add_k_1d_nearest_neighbors_to_dataframe(weather_daily_dataframe, num_matches, exclude_days)

## print wetaher daily dataframe to the excel sheet so we can see the similar days assigned to each day
print "--Printing similar day data to spreadsheet object"+'\n'
weather_daily_dataframe.to_excel(output_book,"WBTSimDays")

## This function takes a df of interval data (multiple readings per day)
## and slices it down to the given dates and returns a df representing a single day
## with the average weekday, average weekend, peak day, and min day
print "--Getting the average day metrics for weather in the performance period"+'\n'
weather_average_day_profile_dataframe_pp=wam.average_daily_metrics(weather_interval_dataframe, start_date_pp, end_date_pp, 'WetBulbTemp')


## Write to excel
print "--Printing weather average day to excel object"+'\n'
weather_average_day_profile_dataframe_pp.to_excel(output_book,"WBTAveDay")


print "--Preparing dataframe for grouping by time"+'\n'
energy_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(energy_interval_dataframe_all, start_date_all, end_date_all)




## Getting this right involves making the column names unique for each set. Should be easy
## Just use the first couple chars of item as column heading.
print "--Getting average day energy profile metrics"+'\n'
df_ave_day_list=[]
for item in column_headings:
    energy_average_day_profile_dataframe_pp=wam.average_daily_metrics(energy_interval_dataframe, start_date_pp, end_date_pp, item)
    df_ave_day_list.append(energy_average_day_profile_dataframe_pp)

if len(df_ave_day_list)==1:
    ave_day_stats_pp=df_ave_day_list[0]
else:  
    ave_day_stats_pp=df_ave_day_list[0].join(df_ave_day_list[1:], how='outer')


print "--Printing ave day stats to excel object."+'\n'
ave_day_stats_pp.to_excel(output_book,"EnergyAveDay")


##------------------------ BAND --------------------------------

print "--Generating band"+'\n'
energy_band_stats_by_day_df_all=wam.get_band_data(energy_interval_dataframe, weather_daily_dataframe, num_matches, num_data_cols, output_book)


energy_band_stats_by_day_df_all.to_excel(output_book,"BandData")


energy_band_stats_by_day_df_pp=energy_band_stats_by_day_df_all[start_date_pp:end_date_pp]
energy_band_stats_by_day_df_pp.to_excel(output_book,"BandDataPP")







##--------------------BUCKETS-------------------------------------------------------


print "--Getting bucketed usage"+'\n'
bucketed_usage_df=wam.bucketed_usage_wrapper(energy_interval_dataframe, df_ave_day_list, num_data_cols, end_date_pp, column_headings, debug, divider)


print "--Printing bucketed usage to excel object"+'\n'
bucketed_usage_df.to_excel(output_book,"Bucketed Usage")


print "--Getting year to date bucketed usage"+'\n'
bucketed_usage_ytd_df=bucketed_usage_df
bucketed_usage_ytd_df['Date']=bucketed_usage_df.index
bucketed_usage_ytd_df['Year']=bucketed_usage_ytd_df['Date'].apply(wam.datetime2year)
bucketed_usage_groups_by_year=bucketed_usage_ytd_df.groupby('Year')
bucketed_usage_list_years=list(bucketed_usage_groups_by_year.groups.iterkeys())
bucketed_usage_max_year=max(bucketed_usage_list_years)
bucketed_usage_ytd_df=bucketed_usage_groups_by_year.get_group(bucketed_usage_max_year)
bucketed_usage_ytd_df=bucketed_usage_ytd_df.iloc[:,0:len(column_headings)*2]


print "--Printing year to date bucketed usage to excel object."+'\n'
bucketed_usage_ytd_df.to_excel(output_book,"Bucketed Usage YTD")




## Getting monthly usage numbers for all streams.
print "--Calculating monthly usages for energy streams"+'\n'
column_dict={}
for i in range(1,len(column_headings)+1):
    column_dict[energy_interval_dataframe.columns[i]]=np.sum
#column_dict={'Electric (kWh)':np.sum,'Steam (lbs)':np.sum}
energy_monthly_dataframe=energy_interval_dataframe.groupby(['Year', 'Month'], sort=False, as_index=False).agg(column_dict)
energy_monthly_dataframe['YearMonth']=energy_monthly_dataframe['Year']*100+energy_monthly_dataframe['Month']
energy_monthly_dataframe=energy_monthly_dataframe.sort('YearMonth')
energy_monthly_dataframe=energy_monthly_dataframe.reset_index()


energy_monthly_df=pd.DataFrame()
energy_monthly_df['Year']=energy_monthly_dataframe['Year']
energy_monthly_df['Month']=energy_monthly_dataframe['Month']

for i in range(len(column_headings)):
    energy_monthly_df[column_headings[i]]=energy_monthly_dataframe[column_headings[i]]

energy_monthly_df=energy_monthly_df.set_index(energy_monthly_dataframe['YearMonth'])

print "--Printing monthly vales to excel object"+'\n'
energy_monthly_df.to_excel(output_book,"Monthly Usage")



##-----------------------------------PEAK WEAK---------------------------------------------------

## Change so that peak week is all put on the same tab. There is no need to have a tab for each month!?!?!?

print "--Getting the peak weak in each month in the performance period for all streams"+'\n'
## A place to put the results
## This will be a list of all streams for all months
peak_week_all_streams_all_months_list=[]

## Group the df of all the data into days to find the appropriate timestamps to use to slice the df with the dates chosen before
performance_group=energy_interval_dataframe.groupby('Date')

## Start timestamp is the min timestamp in the start DATE's set of interval data
start_timestamp=min(performance_group.get_group(start_date_pp).index)
start_month=start_timestamp.month

## End timestamp is the max ts in the enddates's interval data
end_timestamp=max(performance_group.get_group(end_date_pp).index)
end_month=end_timestamp.month

## Slice up the df to get ther performance period df. 
energy_interval_dataframe_pp=energy_interval_dataframe[start_timestamp: end_timestamp]

## Take that and group it by month because we're finding the peak day and surrounding week for each month in the pp
performance_period_group_by_month=energy_interval_dataframe_pp.groupby('Month')


## for every month in the performance period. 
for current_month in range(start_month,end_month+1):
    
    ## Get the single months data
    performance_period_single_month_df=pd.DataFrame(performance_period_group_by_month.get_group(current_month))

    peak_week_all_streams_list=[]

    ## Here is where the second loop should start
    ## I need to get the peak weak for all streams and add it to a list and concatonate it and print it to the
    ## excel file before I can move on to the next month. So close!

    for i in range(1,num_data_cols+1):

        # Get date of max usage
        day_with_max=performance_period_single_month_df[performance_period_single_month_df.columns[i]].idxmax().date()

        # Go back the appropriate number of days
        peak_week_start_date=day_with_max-datetime.timedelta(days=day_with_max.isoweekday())

        # Go forward the appropriate number of days
        peak_week_end_date=day_with_max+datetime.timedelta(days=7-day_with_max.isoweekday()-1)

        ## Use start date to get start timestamp
        peak_week_timestamp_start=min(performance_group.get_group(peak_week_start_date).index)

        ## Use end date to get end timestamp
        try:
            peak_week_timestamp_end=max(performance_group.get_group(peak_week_end_date).index)
            
        except:
            print "It looks like the peak day is in a week that extends passed the performance period"
            peak_week_timestamp_end=end_timestamp

        ## slice the interval_data_df to get the peak week - does this have band info?
        peak_week_interval_data=energy_interval_dataframe[peak_week_timestamp_start: peak_week_timestamp_end]

        ## Add this to the list - need to fix this because there should be multiple lists or a list of lists
        peak_week_all_streams_list.append(pd.DataFrame(peak_week_interval_data[peak_week_interval_data.columns[i]]))


    peak_week_all_streams_all_months_list.append(peak_week_all_streams_list)

    
for month in range(len(peak_week_all_streams_all_months_list)):

    for data_stream in range(len(column_headings)):

        print "--Printing peak weak data to excel object for Month"+str(month+1)+'\n'
        peak_week_all_streams_all_months_list[month][data_stream].to_excel(output_book,"Month"+str(month+1),startcol=(data_stream)*2)


print "--Saving the output book"+'\n'
output_book.save()
output_book.close()#?







##-----------------------------------CALANDERS---------------------------------------------------
output_calendar = pd.ExcelWriter(output_calendar_name)

print "--Printing the calendars to excel in a different book"+'\n'

calendar_tab="Calendars"
col_offset_start=3
row_offset_start=3

row_offset=4
col_offset=col_offset_start
row_delta=8
col_delta=9

for heading in column_headings:
    header=pd.DataFrame([heading])
    header.to_excel(output_calendar, calendar_tab, startcol=col_offset)
    col_offset=col_offset+col_delta

col_offset=col_offset_start

elaps_month=(end_timestamp.year*12+end_timestamp.month)-(start_timestamp.year*12+start_timestamp.month)+1

## This wont handle periods that go across the year boundary
current_date=start_timestamp.date()
for month in range(elaps_month):

    month_marker=pd.DataFrame([current_date])
    month_marker.to_excel(output_calendar, calendar_tab, startrow=row_offset)
    
    calendar_df=wam.get_calendar_from_date(current_date)
    
    current_date=datetime.datetime(current_date.year,current_date.month+1,1)

    for data_col in range(num_data_cols):
        calendar_df.to_excel(output_calendar, calendar_tab, startrow=row_offset, startcol=col_offset)
        col_offset=col_offset+col_delta

    col_offset=col_offset_start
    
    row_offset=row_offset+row_delta

print "--Savings and closing calendar sheet"
output_calendar.save()
output_calendar.close()

print "--Opening calendar sheet with formatter"
wb=load_workbook(output_calendar.path)







#reopen book
#get the tab with the calendars
#use offset plus whatever to get to 0,0 of calendar then use day of week of first day of month to get the first
#cell you'll be coloring. 





## Change so that peak week is all put on the same tab. There is no need to have a tab for each month!?!?!?



    


## Find the max temp and get the date of the corresponding datetime index
#day_with_max=df[df.columns[1]].idxmax().date()

#day_with_max.isoweekday()
#number of day back, then 7-numberofday-1 forward to get the surrounding week. Remember this has to be done on a monthly basis so I first
#would have to group by month which I do above, but I need the interval data, blah blah blah within reach.

## Get the data from that day
#day_with_max_data=group_by_day.get_group(day_with_max)



#---------------------------------------------------------------------------------------------
## LAST THING I NEED TO DO
## Take the performance period dataframe and group it by month
## then for every group, get the sum of usage for that month, the peak demand for that month (which I'll already have)
## And also a new dataframe that is just the peak weak in that month.

## I also need to go in and add up the amount of usage above and below the band for each day?
## I think I might be using days when I'm supposed to be using weeks?

## Then consider automatically generating those calenders because I can use the excel printer to change color and stuff!
#---------------------------------------------------------------------------------------------



## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 


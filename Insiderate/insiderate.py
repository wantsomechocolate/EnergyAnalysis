#############################---------------IMPORTS-------------------#######################

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime, time, os
from marbles import glass as chan

from openpyxl import Workbook, load_workbook
from openpyxl.style import Color, Fill, Border
from openpyxl.cell import Cell



#########################--FUNCTION CALLS THAT NEED GLOBAL VARIABLES--#######################
## I don't know how to pass variables to these column operator functions, they implicitly take
## each term in the column as an argument, but giving them another one wasn't working out. 
def datetime2bday(datetime):
    date=datetime.date()
    
    if date in exclude_days: ## Exclude days is a global variable
        return 'Weekend'
    
    else: pass
    
    day_of_week=datetime.isoweekday()
    
    if day_of_week<=5:
        return 'Weekday'
    
    else:
        return 'Weekend'


##############################---------------PRELIM-------------------#######################

## This allows the program to run completely without user input, or not. 
debug=False

## This is for cosmetic stuff
divider="\n---------------------------------------------------------------------------\n"

## Keep track of the time it takes to do various things
time_list=[]
time_list.append(time.time())

print divider,"-------------------Welcome to Insiderate (In-sid-er-ate)-------------------",divider


##############################-------------FILE LOGISTICS-------------#######################

## Have user navigate to desired book and show them what they chose.
if debug==False: 
    print ("--Please navigate to the .xlsx file containing your data\n")
    filetypes=[("Xlsx Files","*.xlsx")]
    book_name=chan.getPath(os.getcwd(), filetypes)
    print ("--You chose to analyze: "+book_name+'\n')
else:
    book_name='/home/wantsomechocolate/Code/EnergyAnalysis/ZY-IO/Working Input/Three Years/ElecGap.xlsx'
    print ("--Analyzing: "+book_name+'\n')


## Get output book name by adding "results" and a time stamp to the filename
## 'add_to_filename' adds text to file name without affecting the extension
## Maybe shutil can do this better or something.
output_bookname=chan.add_to_filename(book_name,"-Results-"+str(int(time_list[0])))

## This is where all the results will go 
output_book = pd.ExcelWriter(output_bookname)

## Except for the calander results, they go in a different place
output_calendar_name=chan.add_to_filename(book_name,"-Calendars-"+str(int(time_list[0])))

## Tell user the output file name - use output_bookname and not output_book because output_book is a writer object,
## not a string
print ("--Output filepath   : "+output_bookname)


##############################----------DAYS TO EXCLUDE-------------#########################

## The days to exclude are in a seperate text file
print "--Getting list of holidays from text file to exclude them from analysis"+"\n"+divider
path_to_check=os.path.dirname(book_name)
exclude_days=wam.get_excluded_days(path_to_check)


##############################-----------GET WEATHER DATA-----------#########################

## This spreadsheet is shipped with the program and can be updated and maintaned seperate from the energy usage data
weather_book_name='program_data/WeatherData.xlsx'

## Get the weather data wbw is weather workbook
print ("--Reading in weather data"+'\n')
wbw = pd.ExcelFile(weather_book_name)

## Weather only has one tab right now that is referred to using the 0 index
## This means that it is ok to add a tab to this book with hdd/cdd data.
## I will do that soon. 
weather_interval_dataframe_all=wbw.parse(wbw.sheet_names[0])

## I do operations that are easy to do on both columns and pandas indices so here I make sure to have both
weather_interval_dataframe_all=wam.duplicate_first_column_as_index(weather_interval_dataframe_all,'DateTimeStamp')

print ("--Read weather data successfully."+'\n')


##############################-----------GET ENERGY DATA------------#########################

## book_name is the file path given by the user earlier.
wb = pd.ExcelFile(book_name)

print ("--Reading in energy data"+'\n')
energy_interval_dataframe_all=wb.parse(wb.sheet_names[0])

## Get the number of columns of actual data (aka exclude the timestamp column)
num_data_cols=len(energy_interval_dataframe_all.columns)-1

## Get all of the column headings
column_headings=list(energy_interval_dataframe_all.columns)

## Pop off the one you don't need (the first one)
dummy=column_headings.pop(0)

## Same as with weather, make the timestamps a column as well as an index for easier manipulation
energy_interval_dataframe_all=wam.duplicate_first_column_as_index(energy_interval_dataframe_all,'DateTimeStamp')


##############################---------------FILL GAPS-------------------#######################

## This isn't working at the moment. the limit doesn't do what I want, which is to only linear fill if the gap is 4 or less.
## What the below line would do is linear fill up to four gaps. so a gap of 10 readings would turn into a gap of 6 readings.
## There was also a problem using when analyzing more than one stream of data. 
#energy_interval_dataframe_all=energy_interval_dataframe_all.interpolate(limit=4)



##############################-------CONVERGE ON WORKING SET OF DATES---------#######################

## This function takes the datalists and compares the dates to get you a daterange in which you have overlapping data.
## It spits out a lot of print statements telling you different things. It uses the exclude days
## Just to give you a warning that you may be including days in the anlysis that you don't want to. 
lower_bound_date, upper_bound_date = wam.get_lower_and_upper_bound_dates(exclude_days, weather_interval_dataframe_all,
                                                                         energy_interval_dataframe_all)

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


## At this point the user should have their desired dates being analyzed and they should work with the data chosen.
## other wise you have failed. 


## Print some of the user input out so they don't have to record it elsewhere.
summary_metric_headings=["Analysis Period Start","Analysis Period End","Performance Period Start","Performance Period End"]
summary_metric_data=[start_date_all,end_date_all,start_date_pp,end_date_pp]
summary_metric_df=pd.DataFrame(summary_metric_data, summary_metric_headings)

summary_metric_df.to_excel(output_book,"Summary Metrics")



##############################-------NUMBER OF SIMILAR DAYS--------#########################

## How many similar days do you want to return?
print divider+'\n'+"--Similar Days to use when generating the band. For 1 year of data, put 3."+'\n'
print "----For 1.5 years, put 4, for 2 or more years, put 5. 6 is the max"+'\n'
## Set defualt to use in getIntegerInput
default_choice=5
## getIntegerInput(min, max, prompt, default, I don't what that last argument is for)
if debug==False:
    num_matches=chan.getIntegerInput(3,6,"----Just press enter to use the number in brackets ["+str(default_choice)+"]> ",default_choice,[])
else:
    num_matches=default_choice


##############################-------ANALYZING THE WEATHER---------#######################

print ("--Analyzing weather data"+'\n')

## Preparing data from for grouping by various time based criteria

## Slices the weather dataframe down to the analysis period and do some other stuff to make it easier to group by
## various time based metrics
weather_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(weather_interval_dataframe_all, start_date_all, end_date_all)

## The above takes the date column and makes a day,hour,month, whatever column. It can't make the weekday weekend column
## becuase the custom apply function datetime2bday needs a variable in this scope and can't get it as a function
## in another world. I'm sure there is a better way, there's got to be a better way.
weather_interval_dataframe['DayType']=weather_interval_dataframe[weather_interval_dataframe.columns[0]].apply(datetime2bday)


## Group the data by calendar day via the groupby method.
weather_daily_grouping=weather_interval_dataframe.groupby('Date')

## Create a dataframe from the group by taking the mean for each one.
weather_daily_dataframe=weather_daily_grouping[weather_interval_dataframe.columns[1]].agg({'Mean' : np.mean})

## This takes the data frame, uses the index (dates) and the first column of data (average wetbulb temperatures here)
## and then for each number in the list finds the k nearest numbers and their corresponding index (or date)
## It adds those results to the data frame and then returns it.
## If num_matches is 5, the returned dataframe will have 5 additional columns. Each one containing the closest match,
## next closest match etc
weather_daily_dataframe=wam.add_k_1d_nearest_neighbors_to_dataframe(weather_daily_dataframe, num_matches, exclude_days)



## This function takes a df of interval data (multiple readings per day)
## and slices it down to the given dates and returns a df representing a single day
## with the average weekday, average weekend, peak day, and min day

## I MAY HAVE TO DO THIS ON A MONTHLY BASIS.
## this functino could potentially return a list of dataframes, each one an average day profile for each
## calendar month within the performance period.
## Alternatively I could just do the average operating profile stuff completely within excel.
## I think I'm going to go that route. I would print the performance period interval data to the output spreadsheet,
## link it to the template, and then just slice it up there. Using dates entered by the user. That way they don't even have to be
## calendar months. 
weather_average_day_profile_dataframe_pp=wam.average_daily_metrics(weather_interval_dataframe, start_date_pp, end_date_pp, 'WetBulbTemp')

print ("--Printing results to excel workbook object"+'\n')

## print wetaher daily dataframe to the excel sheet so we can see the similar days assigned to each day
#print "--Printing similar day data to spreadsheet object"+'\n'
weather_daily_dataframe.to_excel(output_book,"WBTSimDays")

## Write to excel object
weather_average_day_profile_dataframe_pp.to_excel(output_book,"WBTAveDay")


##############################-------ENERGY AVERAGE DAY STATS---------#######################
#Same as a above, I have to do this monthly, I might just move it over to excel.

print "--Calculating average day operating profile metrics"+'\n'
energy_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(energy_interval_dataframe_all, start_date_all, end_date_all)

## This is a little extra that can't be done in above function because it needs access to the variable exclude days
## and I'm not a good programmer so I did it this way. 
energy_interval_dataframe['DayType']=energy_interval_dataframe[energy_interval_dataframe.columns[0]].apply(datetime2bday)


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


print "--Printing average day operating profile metrics to excel workbook object."+'\n'
ave_day_stats_pp.to_excel(output_book,"EnergyAveDay")



##--------------------- BAND OF EXPECTED USE BASED ON SIMILAR WEATHER USAGE-----------------------------

print "--Generating band"+'\n'
energy_band_stats_by_day_df_all=wam.get_band_data(energy_interval_dataframe, weather_daily_dataframe, num_matches, num_data_cols, output_book)


energy_band_stats_by_day_df_all.to_excel(output_book,"BandData")


energy_band_stats_by_day_df_pp=energy_band_stats_by_day_df_all[start_date_pp:end_date_pp]
energy_band_stats_by_day_df_pp.to_excel(output_book,"BandDataPP")

energy_band_performance_metrics_all=[]
for heading in column_headings:
    
    header=heading[0:4]
    lower_bound=energy_band_stats_by_day_df_pp[header+'-DiffLower'].sum()
    middle_bound=energy_band_stats_by_day_df_pp[header+'-DiffExpected'].sum()
    upper_bound=energy_band_stats_by_day_df_pp[header+'-DiffUpper'].sum()
    actual=energy_band_stats_by_day_df_pp[header].sum()

    lower_bound_percentage=lower_bound/actual
    middle_bound_percentage=middle_bound/actual
    upper_bound_percentage=upper_bound/actual

    energy_band_performance_metrics=[lower_bound_percentage, middle_bound_percentage, upper_bound_percentage]
    energy_band_performance_metrics_all.append(energy_band_performance_metrics)
    

## make df transpose, add to overall metrics print to thing.
energy_band_performance_metrics_all_df=pd.DataFrame(energy_band_performance_metrics_all).transpose()




##--------------------PUT USAGE IN BUCKETS DEPENDING WHEN IT OCCURED AND ITS VOLITILITY-------------------


print "--Getting bucketed usage"+'\n'
bucketed_usage_df, start_stop_list_all=wam.bucketed_usage_wrapper(energy_interval_dataframe, df_ave_day_list, num_data_cols, end_date_pp, column_headings, debug, divider)
# start stop list all is a list with one entry for each stream, the entry containing two dates (start and stop)


start_stop_list_all_df=pd.DataFrame()
for item in start_stop_list_all:
    temp_df=pd.DataFrame(item)
    start_stop_list_all_df=pd.concat([start_stop_list_all_df,temp_df],ignore_index=True)


start_stop_list_all_df=start_stop_list_all_df.transpose()


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


## Turn peak weak info into function in wam. 
##------------------FIND THE PEAK WEAK FOR EACH MONTH IN PERFORMANCE PERIOD-------------------------

print "--Getting the peak weak in each month in the performance period for all streams"+'\n'

peak_week_all_streams_all_months_list, peak_days_all_df, pp_bounds_datetime_list = wam.get_peak_week(energy_interval_dataframe, start_date_pp, end_date_pp, num_data_cols)

peak_week_tab="Peak Week"
peak_week_row_delta=700
peak_week_col_delta=2
    
for month in range(len(peak_week_all_streams_all_months_list)):

    for data_stream in range(len(column_headings)):

        print "--Printing peak weak data to excel object for Month"+str(month+1)+'\n'
        peak_week_all_streams_all_months_list[month][data_stream].to_excel(output_book,peak_week_tab,startcol=(data_stream)*peak_week_col_delta,startrow=month*peak_week_row_delta)




##-----------------------------------CALENDARS---------------------------------------------------


print "--Printing the calendars to excel in a different book because formatting"+'\n'

good_bad_days_all_df=wam.generate_formatted_calendars(output_calendar_name, energy_band_stats_by_day_df_pp, peak_days_all_df, pp_bounds_datetime_list, column_headings)



## -----------------------PRINTING SOME ADDITIONAL METRICS-----------------------

start_timestamp, end_timestamp=pp_bounds_datetime_list

elaps_month=(end_timestamp.year*12+end_timestamp.month)-(start_timestamp.year*12+start_timestamp.month)+1
    
column_offset=3
summary_metrics_all_tab="Summary Metrics"
summary_metrics_all_df=pd.concat([start_stop_list_all_df,energy_band_performance_metrics_all_df, good_bad_days_all_df],ignore_index=True)


summary_metrics_all_index=["Start Time","Stop Time", "Percent Lower Bound", "Percent Middle Bound", "Percent Upper Bound"]
for i in range(elaps_month):
    summary_metrics_all_index.append("GoodBad Month"+str(i+1))

summary_metrics_all_df.insert(0,"Field",summary_metrics_all_index)
summary_metrics_all_df=summary_metrics_all_df.set_index('Field')

summary_metrics_all_df.to_excel(output_book,summary_metrics_all_tab,startcol=column_offset)


## Hackin it.
peak_days_tab="Peak Days"
peak_days_all_df.to_excel(output_book,peak_days_tab)

print "--Saving the results book"+'\n'
output_book.save()
output_book.close()


if debug==True:
    pass
else:
    byebye=raw_input("--Completed successfully, press enter to exit")



#---------------------------------------------------------------------------------------------

## Make it look for a local exclude_days first

## Test cases

## Single gaps in data in performance period, current year, all time.

## Zero values in data for pp, cy, at.

## Larger gaps less than cut off for above cases

## Large gaps greater than cutoff for above cases.

## Full days of data missing

## Missing timestamps. 


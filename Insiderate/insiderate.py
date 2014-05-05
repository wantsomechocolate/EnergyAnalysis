#############################---------------IMPORTS-------------------#######################

import numpy as np, pylab as pl, pandas as pd
import wam as wam, datetime, time, os
from marbles import glass as chan

from openpyxl import Workbook, load_workbook
from openpyxl.style import Color, Fill, Border
from openpyxl.cell import Cell


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
    print "--Please navigate to the .xlsx file containing your data\n"
    filetypes=[("Xlsx Files","*.xlsx")]
    book_name=chan.getPath(os.getcwd(), filetypes)
    print "--You chose to analyze: "+book_name+'\n'
else:
    book_name='/home/wantsomechocolate/Code/EnergyAnalysis/ZY-IO/Working Input/Three Years/ElecGap.xlsx'
    print "--Analyzing: "+book_name+'\n'


## Get output book name by adding "results" and a time stamp to the filename
## 'add_to_filename' adds text to file name without affecting the extension
output_bookname=chan.add_to_filename(book_name,"-Results-"+str(int(time_list[0])))

## This is where all the results will go 
output_book = pd.ExcelWriter(output_bookname)

## Except for the calander results, they go in a different place
output_calendar_name=chan.add_to_filename(book_name,"-Calendars-"+str(int(time_list[0])))

## Tell user the output file name - use output_bookname and not output_book because output_book is a writer object, not a string
print "--Output filepath   : "+output_bookname


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


##############################----------DAYS TO EXCLUDE-------------#########################

## The days to exclude are in a seperate text file
print "--Getting list of holidays from text file to exclude them from analysis"+"\n"+divider
exclude_days=wam.get_excluded_days()


##############################-----------GET WEATHER DATA-----------#########################

## This spreadsheet is shipped with the program and can be updated and maintaned seperate from the energy usage data
weather_book_name='program_data/WeatherData.xlsx'

## Get the weather data
print "--Reading in weather data"+'\n'
wbw = pd.ExcelFile(weather_book_name)

## Weather only has one tab right now that is referred to using the 0 index
weather_interval_dataframe_all=wbw.parse(wbw.sheet_names[0])

#print "--Duplicating the first column and setting as the index."+'\n'
## I do operations that are easy to do on both columns and pandas indices so here I make sure to have both
weather_interval_dataframe_all=wam.duplicate_first_column_as_index(weather_interval_dataframe_all,'DateTimeStamp')

print "Read weather data successfully."


##############################-----------GET ENERGY DATA------------#########################

## book_name is the file path given by the user earlier.
wb = pd.ExcelFile(book_name)

print "--Reading in energy data"+'\n'
energy_interval_dataframe_all=wb.parse(wb.sheet_names[0])

#print "--Getting the number of data columns"+'\n'
num_data_cols=len(energy_interval_dataframe_all.columns)-1

#print "--Get list of data streams"+'\n'
column_headings=list(energy_interval_dataframe_all.columns)
dummy=column_headings.pop(0)

#print "--Make timestamp index and first column"+'\n'
energy_interval_dataframe_all=wam.duplicate_first_column_as_index(energy_interval_dataframe_all,'DateTimeStamp')


##############################---------------FILL GAPS-------------------#######################

## This isn't working at the moment. the limit doesn't do what I want, which is to only linear fill if the gap is 4 or less.
## What the below line would do is linear fill up to four gaps. so a gap of 10 readings would turn into a gap of 6 readings.
## There was also a problem using when analyzing more than one stream of data. 
#energy_interval_dataframe_all=energy_interval_dataframe_all.interpolate(limit=4)



##############################-------CONVERGE ON WORKING SET OF DATES---------#######################

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


## At this point the user should have their desired dates being analyzed and they should work with the data chosen.
## other wise you have failed. 


summary_metric_headings=["Analysis Period Start","Analysis Period End","Performance Period Start","Performance Period End"]
summary_metric_data=[start_date_all,end_date_all,start_date_pp,end_date_pp]
summary_metric_df=pd.DataFrame(summary_metric_data, summary_metric_headings)

summary_metric_df.to_excel(output_book,"Summary Metrics")



##############################-------ANALYZING THE WEATHER---------#######################

print "--Preparing data from for grouping by various time based criteria"+'\n'
## Preparing data from for grouping by various time based criteria

## Slices the weather dataframe down to the analysis period and do some other stuff to make it easier to group by
## various time based metrics
weather_interval_dataframe=wam.prepare_dataframe_for_grouping_by_time(weather_interval_dataframe_all, start_date_all, end_date_all)


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


## Write to excel object
print "--Printing weather average day to excel object"+'\n'
weather_average_day_profile_dataframe_pp.to_excel(output_book,"WBTAveDay")


##############################-------ENERGY AVERAGE DAY STATS---------#######################


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



##------------------FIND THE PEAK WEAK FOR EACH MONTH IN PERFORMANCE PERIOD-------------------------

## Change so that peak week is all put on the same tab. There is no need to have a tab for each month

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

## Slice up the df to get the performance period df. 
energy_interval_dataframe_pp=energy_interval_dataframe[start_timestamp: end_timestamp]

## Take that and group it by month because we're finding the peak day and surrounding week for each month in the pp
performance_period_group_by_month=energy_interval_dataframe_pp.groupby('Month')

max_days_all_streams_all_months=[]

## for every month in the performance period. 
for current_month in range(start_month,end_month+1):

    max_days_all_months=[]
    
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

        max_days_all_months.append(day_with_max)

    max_days_all_streams_all_months.append(max_days_all_months)


    peak_week_all_streams_all_months_list.append(peak_week_all_streams_list)

peak_days_all_df=pd.DataFrame(max_days_all_streams_all_months)

peak_week_tab="Peak Week"
peak_week_row_delta=700
peak_week_col_delta=2
    
for month in range(len(peak_week_all_streams_all_months_list)):

    for data_stream in range(len(column_headings)):

        print "--Printing peak weak data to excel object for Month"+str(month+1)+'\n'
        peak_week_all_streams_all_months_list[month][data_stream].to_excel(output_book,peak_week_tab,startcol=(data_stream)*peak_week_col_delta,startrow=month*peak_week_row_delta)




##-----------------------------------CALANDERS---------------------------------------------------
## output tab
output_calendar = pd.ExcelWriter(output_calendar_name)

print "--Printing the calendars to excel in a different book"+'\n'

calendar_tab="Calendars"

#where does the calendar start on the sheet
col_offset_start=3
row_offset_start=3

row_offset=row_offset_start
col_offset=col_offset_start

# how many rows/cols to skip after each calendar
row_delta=8
col_delta=9

# for each data stream print the name of it to the tab
for heading in column_headings:
    header=pd.DataFrame([heading])
    header.to_excel(output_calendar, calendar_tab, startcol=col_offset)
    col_offset=col_offset+col_delta

col_offset=col_offset_start

# How many calendars to print for each stream
elaps_month=(end_timestamp.year*12+end_timestamp.month)-(start_timestamp.year*12+start_timestamp.month)+1


## This wont handle periods that go across the year boundary

# get first month in performance period
current_date=start_timestamp.date()

# for each month in the performance period
for month in range(elaps_month):

    ## prepare to print the month to so the calendars aren't unlabeled. 
    month_marker=pd.DataFrame([current_date])

    ## actually print it. 
    month_marker.to_excel(output_calendar, calendar_tab, startrow=row_offset)

    ## use modulus and floor to create a calendar dataframe from the date
    calendar_df=wam.get_calendar_from_date(current_date)

    ## for the case when the performance period has december in it
    try:
        current_date=datetime.datetime(current_date.year,current_date.month+1,1)
    except:
        current_date=datetime.datetime(current_date.year+1,1,1)

    ## For each stream, print a calendar across the row (because the calendars will be same for each stream)
    for data_col in range(num_data_cols):
        calendar_df.to_excel(output_calendar, calendar_tab, startrow=row_offset, startcol=col_offset)
        col_offset=col_offset+col_delta

    ## reset column offset
    col_offset=col_offset_start

    ## increment row_offset
    row_offset=row_offset+row_delta

## save document
print "--Savings and closing calendar sheet"+'\n'
output_calendar.save()
output_calendar.close()

## open the spreadsheet so that it can be formatted. 
print "--Opening calendar sheet with formatter"+'\n'
wb=load_workbook(output_calendar.path)
ws=wb.get_sheet_by_name(calendar_tab)


Color.CGGREEN='8BBE2F'
Color.CGRED='D63E29'
Color.CGGREY='605650'
Color.CGBKGD='F2F2F2'








start_date=start_timestamp.date()
good_bad_days_all=[]
for i in range(num_data_cols):

    
    ## get the band info for the first data stream
    band_info_df=pd.DataFrame(energy_band_stats_by_day_df_pp[column_headings[i][:4]+'-RGB'])
    ## prepare to organize by month
    band_info_df.insert(0,"Date",band_info_df.index)
    ## add a month column
    band_info_df['Month']=band_info_df[band_info_df.columns[0]].apply(wam.datetime2fdom)
    ## group based on month
    band_info_groups=band_info_df.groupby('Month')

    current_date=start_date

    # a place to put the good bad info for a single stream for all the months in the performance period
    good_bad_days_months=[]
    
    for j in range(elaps_month):

        try:
            fdonm=datetime.date(current_date.year, current_date.month+1,1)
        
            dim=(fdonm-current_date).days

        except:
            dim=31
        
        fdow=current_date.isoweekday()

        group_data=band_info_groups.get_group(current_date)


        good_bad_days=[]
        try:
            
            good_bad_days.append(group_data[column_headings[i][:4]+'-RGB'].value_counts()[-1])
        except:
            good_bad_days.append(0)

        try:
            good_bad_days.append(group_data[column_headings[i][:4]+'-RGB'].value_counts()[1])
        except:
            good_bad_days.append(0)

        good_bad_days_months.append(good_bad_days)
        
        peak_day_for_iter=peak_days_all_df[i][j].day-1
        
        for k in range(dim):
            
            index=k+fdow
            
            row=(int(index/7))+row_offset_start+(row_delta*j)+1

            col=(index%7)+col_offset_start+(col_delta*i)+1

            c=ws.cell(row=row, column=col)
            
            color=group_data[group_data.columns[1]][k]
            
            if color==-1:
                c.style.font.color.index = Color.CGGREEN
                
            elif color==1:
                c.style.font.color.index = Color.CGRED
                
            else:
                c.style.font.color.index = Color.CGGREY

            ## Instead of looping through if a bajillion times, I should go in after and apply the border
            ## I did it this way because I'm lazy. 
            if k==peak_day_for_iter:
                print "HEEELLLLLOOOOOOO"
                c.style.borders.top.border_style=Border.BORDER_THIN
                c.style.borders.bottom.border_style=Border.BORDER_THIN
                c.style.borders.left.border_style=Border.BORDER_THIN
                c.style.borders.right.border_style=Border.BORDER_THIN
                #c.style.borders.color.index=Color.CGRED
                c.style.borders.top.color.index=Color.CGRED
                c.style.borders.bottom.color.index=Color.CGRED
                c.style.borders.left.color.index=Color.CGRED
                c.style.borders.right.color.index=Color.CGRED

        try:
            current_date=datetime.date(current_date.year,current_date.month+1,1)
        except:
            current_date=datetime.date(current_date.year+1,1,1)

    good_bad_days_all.append(good_bad_days_months)

good_bad_days_all_df_inter=pd.DataFrame(good_bad_days_all).transpose()

good_bad_days_all_df=pd.DataFrame()
for col in good_bad_days_all_df_inter:
	good_bad_days_all_df[col]=good_bad_days_all_df_inter[col].apply(str)

## good bad_days_all contains one item per stream, the item contains as many items as months in the performance period
## each of those items contain two number, one for good days and one for bad days. 

## This just turns all the backgrounds grey in the cells for the calendar and changed the font size and stuff. 
for i in range(num_data_cols):

    current_date=start_date
    
    for j in range(elaps_month):

        for k in range(42):
            
            index=k
            
            row=(int(index/7))+row_offset_start+(row_delta*j)+1

            col=(index%7)+col_offset_start+(col_delta*i)+1

            c=ws.cell(row=row, column=col)
            c.style.font.bold=True
            c.style.fill.fill_type=Fill.FILL_SOLID
            c.style.fill.start_color.index = Color.CGBKGD
            c.style.font.name='Century Gothic'
            c.style.font.size=10
            if c.value==0:
                c.value=""
            else:
                pass

print "--Saving the calendar workbook"+'\n'
try:
    wb.save(output_calendar.path)
except:
    print "--Calendar book could not be saved, calendars will have to be manually generated"



## creating the summary metric dataframe
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


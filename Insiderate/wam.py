import datetime
import os, time
import numpy as np
from marbles import glass as chan
from openpyxl import Workbook
from openpyxl import load_workbook
import wam as wam
from dateutil import parser
import pandas as pd
import re



def get_excluded_days():

    ## this filename is hardcoded in, the file will be shipped with
    ## the program so that users can add to it. 
    filename='exclude_days.txt'
    fh=open(filename,'r')
    contents=fh.readlines()
    exclude_days=[]
    for item in contents:
        if len(item.split())>0:
            exclude_days.append(parser.parse(item.split()[0]).date())
    fh.close()
    return exclude_days



def add_k_1d_nearest_neighbors_to_dataframe(data_frame_def,n_count_def,exclude_days_def):

    ## For every number in this list, I need to find the n closest numbers from the same list
    list_of_nums_def=data_frame_def[data_frame_def.columns[0]]
    #print "list of nums length: "+ str(len(list_of_nums_def))

    ## But each number is associated with a date and I can only choose numbers from the same day of the week
    ## and there some days that are excluded for being holidays.
    criteria_date_def=data_frame_def.index
    #print "criteria date list length: "+str(len(criteria_date_def))

    
    ## Initialize an array to get the indices of the matches for the n numbers for each number in the list
    indices_of_matches_def=[]

    ## For each item in the list that this thing is supposed to find the n closest matches for. 
    for i in range(len(list_of_nums_def)):


        list_index_def=[] ## This should be renamed to something else. 
        difference_def=[] 
        min_indices_def=[]
        diff_list_def=[]


        ## Iterate again through the list so that each item can be compared with every other item
        for j in range(len(list_of_nums_def)):

            ## If the current config is good (same day of week, not same date, not holiday
            if (criteria_date_def[i].isoweekday()==criteria_date_def[j].isoweekday()) and (i!=j) and (criteria_date_def[j] not in exclude_days_def):

                ## append the list index of the wetbulb that is a potential candidate
                ## this list will have a length of around 50 for every year of data used.
                list_index_def.append(j)

                ## try to get the absolute value of the difference between metrics for comparison
                ## This above list holds indices, this list will hold the difference in the numbers
                ## for each of those indices
                ## The try block is in case the list number isn't a number
                try:
                    difference_def.append(abs(list_of_nums_def[i]-list_of_nums_def[j]))
                except:
                    difference_def.append("err")

        ## populate diff_list with what is described above. diff list will be a list of two lists
        ## of the same lenth - one with indices in the original master list and one with abs diff
        ## the list for each iteration through days of the year will only contain days that land
        ## on the same day of the week; aren't holidays)
        diff_list_def=[list_index_def,difference_def]


        ## For each of the closest days that this function is supposed to find
        for n in range(n_count_def):
            ## This is essentially making a list of 0's with the length to fit all the closest days
            min_indices_def.append(0)
        
        ## For each of the N values I'm supposed to get from the diff list.
        for k in range(len(min_indices_def)):

            ## Find the min (closest value to current days) the first time through, this will likely
            ## BE the current day. except for the fact that I excluded that from being a candidate day above.

            ## out of the abs diff list, which has the lowest error
            min_val_def=min(diff_list_def[1])

            ## then get the index of that minimum value in diff_list[i]
            index_of_min_val_in_diff_list_def=diff_list_def[1].index(min_val_def)

            ## Then get master list index associated with that diff list index
            day_of_year_min_val_occurred_def=diff_list_def[0][index_of_min_val_in_diff_list_def]

            ## then save the INDEX of the min value
            min_indices_def[k]=day_of_year_min_val_occurred_def

            ## Then alter diff_list so that the value at the saved index is no longer even
            ## close to being a match. aka a string
            diff_list_def[1][index_of_min_val_in_diff_list_def]="already matched"

        ## Add the indices (a list) to a bigger list that will hold a list of the N closest values
        ## for each day. 
        #min_indices_list.append(min_indices)

        indices_of_matches_def.append(min_indices_def)

    ## Because the above returns a list of list indices instead of a list of datetime objects
    ## Use those indicies to get the corresponding datetime objects.

    ## make list of right dimension
    similar_days_by_DATE=[]
    for i in range(len(indices_of_matches_def)):
        similar_days_by_DATE.append([])


    for i in range(len(indices_of_matches_def)):
        for j in range(len(indices_of_matches_def[i])):
            similar_days_by_DATE[i].append(criteria_date_def[indices_of_matches_def[i][j]])

    

    indices_of_matches_def_zipped = zip(*indices_of_matches_def)
    similar_days_by_DATE_zipped = zip(*similar_days_by_DATE)



    ave_wbt_of_similar_days=[]
    for i in range(n_count_def):
        ave_wbt_of_similar_days.append([])

    for i in range(len(indices_of_matches_def_zipped)):
        for j in range(len(indices_of_matches_def_zipped[i])):
            ave_wbt_of_similar_days[i].append(list_of_nums_def[indices_of_matches_def_zipped[i][j]])


    ## Add back to data frame

    for col in range(len(similar_days_by_DATE_zipped)):
        data_frame_def['Date '+str(col+1)]=similar_days_by_DATE_zipped[col]
        #data_frame_def['Mean '+str(col+1)]=ave_wbt_of_similar_days[col]

##    ## add to dataframe
    for col in range(len(ave_wbt_of_similar_days)):
        data_frame_def['Mean '+str(col+1)]=ave_wbt_of_similar_days[col]
        

    return data_frame_def




def duplicate_first_column_as_index(df, column_name):

    ## Set the first column as the index
    df=df.set_index(df.columns[0])

    ## Insert a new column of data at position 0 using the index as the data
    df.insert(0,column_name,df.index)

    return df



## To map a datetime column in a pandas dataframeto a date column
def datetime2date(datetime):
    return datetime.date()

def datetime2hour(datetime):
    hour=datetime.hour
    minute=datetime.minute
    return hour*4+minute/15
    #return datetime.hour

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

def datetime2month(datetime):
    return datetime.month

def datetime2year(datetime):
    return datetime.year



## I didn't know how to pass a function with variables to the agg operator so
## so I had to define it in the top level of my module :(
exclude_days=get_excluded_days()
def prepare_dataframe_for_grouping_by_time(df, sd, ed):

    ## Get slice that will be used for band analysis (1-3 years most likely)
    #df=df[sd:ed]
    
    ## From the datetime in column one, make a new column with only the date portion of each date time, for grouping
    df['Date']=df[df.columns[0]].apply(datetime2date)

    ## Add hour column
    df['Hour']=df[df.columns[0]].apply(datetime2hour)

    df['Month']=df[df.columns[0]].apply(datetime2month)

    df['Year']=df[df.columns[0]].apply(datetime2year)

    ## Add a daytype that seperates days into Weekday and Holiday/Weekend
    df['DayType']=df[df.columns[0]].apply(datetime2bday)

    ## get first time stamp in group that is the start date
    group=df.groupby('Date')
    
    start_timestamp=min(group.get_group(sd).index)

    end_timestamp=max(group.get_group(ed).index)

    df=df[start_timestamp: end_timestamp]

    return df



def prepare_df_indexed_by_time_for_grouping_by_day(df):
    print "filler"



def average_daily_metrics(df, sd, ed, col_name):


    group=df.groupby('Date')
    start_timestamp=min(group.get_group(sd).index)
    end_timestamp=max(group.get_group(ed).index)


    df=df[start_timestamp: end_timestamp]


    ## Now I'm interested only in performance period
    #df=df[sd:ed]

    identifier=col_name[:4]

    ## In one swoop, group by daytype and hour, get the averages for each group, then put back into df
    df_ave_day=df.groupby(['DayType', 'Hour'], sort=False, as_index=False).agg({col_name:np.mean})

    ## Now group based on the new df
    groups=df_ave_day.groupby('DayType')

    ## I know there will be two groups because of what the datetime to business day function does.
    weekday=groups.get_group('Weekday')[col_name]
    weekend=groups.get_group('Weekend')[col_name]

    ## Create new df with groups as columns
    df_ave_day=pd.DataFrame({identifier+'-Weekday':weekday.values,identifier+'-Weekend':weekend.values})

    ## Group by day so that I can use the max day as a key to get the data for the max day
    group_by_day=df.groupby('Date')



    ## Group by date to get the max and min day
    mean_by_day=group_by_day[col_name].agg(np.mean)

    max_day=mean_by_day.idxmax()
    min_day=mean_by_day.idxmin()

    max_day_data=group_by_day.get_group(max_day)
    min_day_data=group_by_day.get_group(min_day)



    ## Find the max temp and get the date of the corresponding datetime index
    day_with_max=df[df.columns[1]].idxmax().date()

    ## Get the data from that day
    day_with_max_data=group_by_day.get_group(day_with_max)

    ## Find the min temp and get the date of the corresponding datetime index
    day_with_min=df[df.columns[1]].idxmin().date()

    ## Get the data from that day
    day_with_min_data=group_by_day.get_group(day_with_min)

    ## Using the string for the date of the max day as the heading, add values to df
    df_ave_day[identifier+"-"+str(day_with_max)+"-DayWithMax"]=day_with_max_data[day_with_max_data.columns[1]].values

    ## Using the string for the date of the min day as the heading, add values to df
    df_ave_day[identifier+"-"+str(day_with_min)+"-DayWithMin"]=day_with_min_data[day_with_min_data.columns[1]].values


    df_ave_day[identifier+"-"+str(max_day)+"-MaxDay"]=max_day_data[max_day_data.columns[1]].values

    df_ave_day[identifier+"-"+str(min_day)+"-MinDay"]=min_day_data[min_day_data.columns[1]].values

    return df_ave_day



def get_ave_of_k_min_values(list_to_take_mins_from_all_def,num_of_min_values_def,index_start_def, index_end_def):

    ## This is done in case you want to look at a beginning of the day baseline and not have crazy
    ## end of the day stuff get in the way.
    
    list_to_take_mins_from_def=list_to_take_mins_from_all_def[index_start_def:index_end_def]

    if len(list_to_take_mins_from_def)<num_of_min_values_def:
        return np.average(list_to_take_mins_from_def)

    else:
        k_min_values_def=[]
        list_to_take_mins_from_copy_def=list(list_to_take_mins_from_def)
        for i in range(num_of_min_values_def):
            min_value_def=min(list_to_take_mins_from_copy_def)
            list_to_take_mins_from_copy_def.remove(min_value_def)
            k_min_values_def.append(min_value_def)

        try:
            k_min_average_def=np.average(k_min_values_def)
        except:
            k_min_average_def="Not enough min values"

        return k_min_average_def


def get_baseline_by_day(list_of_usages_by_day_def,num_values_def, start_index_def, end_index_def):
    
    baseline_by_day_def=[]
    for i in range(len(list_of_usages_by_day_def)):
        baseline_by_day_def.append([])

    for i in range(len(list_of_usages_by_day_def)):
        baseline_def=get_ave_of_k_min_values(list_of_usages_by_day_def[i],num_values_def, start_index_def, end_index_def)
        for j in range(len(list_of_usages_by_day_def[i])):
            baseline_by_day_def[i].append(baseline_def)

    return baseline_by_day_def



def get_date_range_from_user(debug_mode=False):

    if debug_mode==False:
        from dateutil import parser

        got_to_end=False
        while got_to_end==False:
            try:
                start_date=raw_input("--Start Date - All common formats are fine, use full year: ")
                sd_obj=parser.parse(start_date)
                sd_obj=sd_obj.date()
                got_to_end=True
            except:
                print "--Date format not recognized or date does not exist"

        got_to_end=False
        while got_to_end==False:
            try:
                end_date=raw_input("--End Date - All common formats are fine, use full year: ")
                ed_obj=parser.parse(end_date)
                ed_obj=ed_obj.date()
                if sd_obj<ed_obj:
                    got_to_end=True
                else:
                    print "--What! enter the dates in order, fool!"
            except:
                print "--Date format not recognized or date does not exist"

        return [sd_obj, ed_obj]

    else:
        return [datetime.datetime(2013,7,1), datetime.datetime(2013,9,30)]



def get_bucket_date_range_from_user(end_date=""):
    #bucket_end_date_text="6/30/2013"

##    bucket_end_date_text=raw_input("What is the end date of the year you want to use for bucket analysis? >>> ")
##    
##    bucket_end_date=parser.parse(bucket_end_date_text)

    if end_date=="":
        got_to_end=False
        while got_to_end==False:
            try:
                bucket_end_date_text=raw_input("What is the end date of the year you want to use for bucket analysis? >>> ")
                if len(bucket_end_date_text)<=5:
                    error="str"+5
                else:
                    bucket_end_date=parser.parse(bucket_end_date_text)
                    got_to_end=True
            except:
                print "Date format not recognized or date does not exist"

    else:
        bucket_end_date=end_date

            
    while bucket_end_date.isoweekday()!=1:
        bucket_end_date=bucket_end_date-datetime.timedelta(days=1)

    bucket_start_date=bucket_end_date-datetime.timedelta(days=364)

    return [bucket_start_date, bucket_end_date]



def get_operating_hours_from_user(debug=False):

    re_time_hh_mm='[012][0123456789]:[012345][1234567890]'

    bucket_start_day_text="00:00"

    bucket_end_day_text="23:45"


    if debug==False:
    
        flag=0
        while flag==0:
            bucket_closed_to_open_text=raw_input("--At what time does the building go from CLOSED to OPEN? (HH:MM) >>> ")

            if len(bucket_closed_to_open_text)>5:
                print "That input is too long to be in the right format"

            else:
                try:
                    bucket_closed_to_open_text=re.search(re_time_hh_mm,bucket_closed_to_open_text).group()
                    flag=1
                except:
                    print "The time you entered was not in the correct format, or was not a time"

        flag=0
        while flag==0:
            bucket_open_to_closed_text=raw_input("--At what time does the building go from OPEN to CLOSED? (HH:MM) >>> ")

            if len(bucket_open_to_closed_text)>5:
                print "That input is too long to be in the right format"

            else:
                try:
                    bucket_open_to_closed_text=re.search(re_time_hh_mm,bucket_open_to_closed_text).group()
                    flag=1
                except:
                    print "The time you entered was not in the correct format, or was not a time"
    else:
        print "debug mode is on for this function. Buckut hours are 6am-6pm"
        bucket_closed_to_open_text='06:00'
        bucket_open_to_closed_text='18:00'
        


    bucket_start_day=parser.parse(bucket_start_day_text)
    bucket_end_day=parser.parse(bucket_end_day_text)
    
    bucket_closed_to_open_time=parser.parse(bucket_closed_to_open_text)
    bucket_open_to_closed_time=parser.parse(bucket_open_to_closed_text)

    
    if bucket_closed_to_open_time<bucket_open_to_closed_time:
        bucket_specifying_open_or_closed="open"
        bucket_start_time=bucket_closed_to_open_time
        bucket_end_time=bucket_open_to_closed_time
    else:
        bucket_specifying_open_or_closed="closed"
        bucket_start_time=bucket_open_to_closed_time
        bucket_end_time=bucket_closed_to_open_time

    bucket_current_time=bucket_start_day
    bucket_open_closed=[]

    while bucket_current_time<=bucket_end_day:
        
        if bucket_current_time<bucket_start_time or bucket_current_time>=bucket_end_time:
            if bucket_specifying_open_or_closed=="open":
                bucket_open_closed.append(0)
            else:
                bucket_open_closed.append(1)
        else:
            if bucket_specifying_open_or_closed=="open":
                bucket_open_closed.append(1)
            else:
                bucket_open_closed.append(0)
                
        bucket_current_time=bucket_current_time+datetime.timedelta(minutes=15)    

    return bucket_open_closed
    



def get_bucketed_usage(bucket_operating_hours_by_day_def, date_list_def, start_date_index_def, end_date_index_def,
                       interval_usage_by_day_def):

    bucket_open_usage_def=[]
    bucket_closed_usage_def=[]
    bucket_date_def=[]
    
    intermediate_week_open=0
    intermediate_week_closed=0

    for i in range(start_date_index_def, end_date_index_def):
        
        if date_list_def[i].isoweekday()<6:

            for j in range(len(bucket_operating_hours_by_day_def[i-start_date_index_def])):
                if bucket_operating_hours_by_day_def[i-start_date_index_def][j]==1:
                    try:
                        intermediate_week_open+=interval_usage_by_day_def[i][j]
                    except:
                        print "Interval Usage did not evaluate to be an integer"
                        print "Day: ",
                        print date_list_def[i],
                        print "Time: ",
                        print (j+1)/4.0
                else:
                    try:
                        intermediate_week_closed+=interval_usage_by_day_def[i][j] ##------------What the fuck is going on
                    except:
                        print "Interval Usage did not evaluate to be an integer",
                        print "Day: ",
                        print date_list_def[i],
                        print "Time: ",
                        print (j+1)/4.0
                        
        if date_list_def[i].isoweekday()==7:

            bucket_date_def.append(date_list_def[i])
            
            bucket_open_usage_def.append(intermediate_week_open)
            bucket_closed_usage_def.append(intermediate_week_closed)
            
            intermediate_week_open=0
            intermediate_week_closed=0

    return [bucket_open_usage_def, bucket_closed_usage_def, bucket_date_def]









#### This function takes a list of lists and another list of lists and groups the first list based
#### on the indices in the second one?
##def use_list_of_list_of_indices_to_group_a_list_of_lists(main_list_def,list_of_list_indices_def):
##
##    main_list_with_criteria_def=[]
##
##    ## for item in sim days by day (each item will be a list of ints corresponding to list indices)
##    for i in range(len(list_of_list_indices_def)):
##
##        ## an interim variable to hold a single day?
##        interim_list_def=[]
##
##        ## for each list index corresponding to day of year
##        for j in range(len(list_of_list_indices_def[i])):
##
##            ## Go to list with the data you want and collect it
##            interim_list_def.append(main_list_def[list_of_list_indices_def[i][j]])
##
##        ## put all the days usages collected into the final list
##        main_list_with_criteria_def.append(interim_list_def)
##
##        ## the result of this is a list of 366 days, each day has N similar days in it, each similar day has 96 values. 
##
##    return main_list_with_criteria_def



##def zip_all_items_of_a_list(list_to_zip_def):
##    zipped_list_def=[]
##    for item in list_to_zip_def:
##        zipped_list_def.append(zip(*item))
##
##    return zipped_list_def



##def get_ave_std_of_list_of_list_of_list(list_to_analyze_def):
##
##    list_average_def=[]
##    list_std_def=[]
##    list_average_plus_stdev_def=[]
##    list_average_minus_stdev_def=[]
##
##    for list_of_list_def in list_to_analyze_def:
##        inter_list_ave_def=[]
##        inter_list_std_def=[]
##        inter_list_stdup_def=[]
##        inter_list_stdlo_def=[]
##        for list_ in list_of_list_def:
##
##            inter_def=np.array(list_)
##
##            
##            inter_def_new=[]
##            for item in inter_def:
##                try:
##                    inter_def_new.append(float(item))
##                except:
##                    pass
##            inter_def=np.array(inter_def_new)
##
##            
##            inter_list_ave_def.append(inter_def.mean())
##            inter_list_std_def.append(inter_def.std())
##            inter_list_stdup_def.append(inter_def.mean()+inter_def.std())
##            inter_list_stdlo_def.append(inter_def.mean()-inter_def.std())
##
##
##                
##
##                
##        list_average_def.append(inter_list_ave_def)
##        list_std_def.append(inter_list_std_def)
##        list_average_plus_stdev_def.append(inter_list_stdup_def)
##        list_average_minus_stdev_def.append(inter_list_stdlo_def)
##
##    return_list_def=[list_average_def,list_average_plus_stdev_def,list_average_minus_stdev_def,list_std_def]
##
##    return return_list_def



##def get_start_time_each_day(interval_time_by_day_def,interval_usage_by_day_def, baseline_by_day_def, percent_above_baseline_def, threshold_def):
##
##    ## for every day
##    start_time_each_day_def=[]
##    
##    for i in range(len(interval_usage_by_day_def)):
##
##        found_start_time_def="No"
##        start_time_def="default value"
##        count=0
##
##        ## for every 15 minute period
##
##        if "Not enough min values" in baseline_by_day_def[i]:
##            start_time_each_day_def.append("Not enough min values")
##        else:
##        
##            for j in range(len(interval_usage_by_day_def[i])):
##                
##
##                ##if the usage during the 15 minutes is greater than a percentage more than the baseline
##                if interval_usage_by_day_def[i][j]>baseline_by_day_def[i][j]*(1+percent_above_baseline_def):
##                    ## increase count
##                    count=count+1
##                else:
##                    ## otherwise reset count
##                    count=0
##
##                ## at this point, count could be from 0 to 96 (every value higher than baseline)
##
##                ## if at any point it becomes greater than thresh and it hasn't before today
##                if count>=threshold_def and found_start_time_def=="No":
##                    ## say that the start time occured when the increase started
##                    start_time_def=interval_time_by_day_def[i][j-threshold_def]
##
##                    ## and say that a start time was found for the day
##                    found_start_time_def="Yes"
##
##            if found_start_time_def=="Yes":
##                if start_time_def.hour==0:
##                    start_time_each_day_def.append("err")
##                else:
##                    start_time_each_day_def.append(start_time_def)
##            else:
##                start_time_each_day_def.append("N/A")
##
##
##    return start_time_each_day_def



##def get_end_time_each_day(interval_time_by_day_def, interval_usage_by_day_def, baseline_by_day_def, start_time_each_day_def, percent_above_baseline_def, thresh_end_def):
##
##    end_time_each_day_def=[]
##    
##    start_time_each_day_copy=list(start_time_each_day_def)
##
##    ## for every day
##    for i in range(len(interval_usage_by_day_def)):
##
##        ## Refresh some vars
##        found_end_time_def="No"
##        end_time_def="default val"
##        count=0
##
##        if "Not enough min values" in baseline_by_day_def[i]:
##            end_time_each_day_def.append("Not enough min values")
##        else:
##
##
##            ## for every 15 minute period
##            for j in range(len(interval_usage_by_day_def[i])):
##
##
##                try:
##                    test=start_time_each_day_copy[i].hour
##                except:
##                    start_time_each_day_copy[i]=interval_time_by_day_def[i][40]
##
##                ## If the 15 minute period in question is not even passed the start time
##                if interval_time_by_day_def[i][j]<=start_time_each_day_copy[i]:
##
##                    ## Then don't do anything. 
##                    pass
##
##                ## Otherwise, begin/continue the analysis. 
##                else:
##                
##                    ##if the usage during the 15 minutes is less than a percentage more than the baseline
##                    if interval_usage_by_day_def[i][j]<baseline_by_day_def[i][j]*(1+percent_above_baseline_def):
##                        ## increase count
##                        count=count+1
##                    else:
##                        ## otherwise reset count
##                        count=0
##
##                    ## at this point, count could be from 0 to 96 minus the number of points that fell before the start time
##
##                    ## if at any point it becomes greater than or equal to thresh and it hasn't before today
##                    if count>=thresh_end_def and found_end_time_def=="No":
##                        
##                        ## say that the end time occured when thresh was met
##                        end_time_def=interval_time_by_day_def[i][j-thresh_end_def]
##
##                        ## and say that an end time was found for the day
##                        found_end_time_def="Yes"
##
##            if found_end_time_def=="Yes":
##        ##            if end_time.hour==0:
##        ##                end_time_each_day.append("err")
##        ##            else:
##                end_time_each_day_def.append(end_time_def)
##            else:
##                ## the case that the program gets here on the last element of the array being indexed by i
##                ## needs to be coded for. 
##                ## If it fails it most likely means that the end time occurs the next day - at least for the data set that I'm using.
##
##                try:
##
##                    for m in range(len(interval_usage_by_day_def[i+1])): #next day
##                        if found_end_time_def=="No":
##                            if interval_usage_by_day_def[i+1][m]<baseline_by_day_def[i+1][m]*(1+percent_above_baseline_def):
##                                found_end_time_def="Yes"
##                                end_time_def=interval_time_by_day_def[i+1][m]
##
##                ## Last Day no Shutdown
##                except:
##                    end_time_def="LDNSD"
##                    
##                end_time_each_day_def.append(end_time_def)
##
##    return end_time_each_day_def



##def get_stats_by_day_in_range(interval_usage_by_day_def, date_list_def, date_range_def):
##    
##    start_index_def=date_list_def.index(date_range_def[0])
##    end_index_def=date_list_def.index(date_range_def[1])
##
##    #interval_by_day_in_range_def=interval_by_day_def[start_index_def:end_index_def]
##
##
##    date_list_wkday_def=[]
##    date_list_wkend_def=[]
##    interval_wkday_def=[]
##    interval_wkend_def=[]
##
##    max_value_reached_def=0
##
##    #print start_index_def
##    #print end_index_def
##    
##    for i in range(start_index_def, end_index_def):
##        
##        if date_list_def[i].weekday()<=4:
##            date_list_wkday_def.append(date_list_def[i])
##            interval_wkday_def.append(interval_usage_by_day_def[i])
##        else:
##            date_list_wkend_def.append(date_list_def[i])
##            interval_wkend_def.append(interval_usage_by_day_def[i])
##
##
##        max_val_by_day_def=max(interval_usage_by_day_def[i])
##        if max_val_by_day_def>max_value_reached_def:
##            max_value_reached_def=max_val_by_day_def
##            peak_day_usage_def=interval_usage_by_day_def[i]
##            peak_date_def=date_list_def[i]
##        else:
##            pass
##        
##
##
##    interval_wkday_zipped_def=zip(*interval_wkday_def)
##    interval_wkend_zipped_def=zip(*interval_wkend_def)
##
##
##    wkday_ave_def=[]
##    for item in interval_wkday_zipped_def:
##        item_np_def=np.array(item)
##        item_ave_def=item_np_def.mean()
##        wkday_ave_def.append(item_ave_def)
##
##    wkend_ave_def=[]
##    for item in interval_wkend_zipped_def:
##        item_np_def=np.array(item)
##        item_ave_def=item_np_def.mean()
##        wkend_ave_def.append(item_ave_def)
##
##    return [wkday_ave_def,wkend_ave_def,peak_day_usage_def,peak_date_def]





## ----------------This is done by pandas now---------------------
##def interval2day(interval_data_def):
##
##
##    number_of_non_date_columns_def=len(interval_data_def[1:])
##    
##    number_of_columns_def=len(interval_data_def)
##
##    ## The datetime is assumed to be the first list 
##    datetime_list_def=interval_data_def[0]
##
##    ## Create space for the lists of data (exclude the date)
##    data_lists_def=[]
##
##    ## Now I have a list of at least one other list, but possibly more
##    for i in range(1,number_of_columns_def):
##        
##        data_lists_def.append(interval_data_def[i])
##
##
##    ## Get the first date (assumed to be the earliest date)
##    current_date_def=datetime.datetime(datetime_list_def[0].year, datetime_list_def[0].month, datetime_list_def[0].day)
##
##    ## Get the last date (assumed to be the most recent date)
##    end_date_def=datetime.datetime(datetime_list_def[-1].year, datetime_list_def[-1].month, datetime_list_def[-1].day)
##
##    ## Prepare for creation of date list
##    date_list_def=[]
##    
##    ## This is done this way at the moment in case there are missing dates, at least every day will still have
##    ## a space allocated for it. 
##    while current_date_def<=end_date_def:
##        date_list_def.append(current_date_def)
##        current_date_def=current_date_def+datetime.timedelta(days=1)
##
##    ## Make a number of unique lists
##    unique_lists=[]
##    for i in range(number_of_columns_def):
##        unique_lists.append([])
##        for j in range(len(date_list_def)):
##            unique_lists[i].append([])
##
##    datetime_list_by_day_def=unique_lists[0]
##                                   
##    data_lists_by_day_def=[]
##    ## For as many columns of data there are
##    for i in range(1,number_of_columns_def):
##        ## Make room for that column of data to be sorted by day
##        data_lists_by_day_def.append(unique_lists[i])
##
##        
##    ## Go through the huge list and put everything where it goes.
##    ## FOR EVERY SINGLE DATA POINT in the original datetime list
##    for i in range(len(datetime_list_def)):
##
##        ## Strip the time off of the datetime in the interval datetime list
##        interval_data_day_def=datetime.datetime(datetime_list_def[i].year,datetime_list_def[i].month,datetime_list_def[i].day)
##
##        ## Then find the index for that day in the date list
##        index_def=date_list_def.index(interval_data_day_def)
##        #print index_def
##
##        datetime_list_by_day_def[index_def].append(datetime_list_def[i])
##
##        for k in range(len(interval_data_def[1:])):
##            data_lists_by_day_def[k][index_def].append(data_lists_def[k][i])
##                                       
##    return_list_def=[]
##
##    for i in range(len(interval_data_def[1:])):
##        return_list_def.append([datetime_list_by_day_def,data_lists_by_day_def[i]])
##
##    return return_list_def



##def interval2dayPandas(interval_data_def):
##
##
##    number_of_non_date_columns_def=len(interval_data_def[1:])
##    
##    number_of_columns_def=len(interval_data_def)
##
##    ## The datetime is assumed to be the first list 
##    datetime_list_def=interval_data_def[0]
##
##    ## Create space for the lists of data (exclude the date)
##    data_lists_def=[]
##
##    ## Now I have a list of at least one other list, but possibly more
##    for i in range(1,number_of_columns_def):
##        
##        data_lists_def.append(interval_data_def[i])
##
##
##    ## Get the first date (assumed to be the earliest date)
##    current_date_def=datetime.datetime(datetime_list_def[0].year, datetime_list_def[0].month, datetime_list_def[0].day)
##
##    ## Get the last date (assumed to be the most recent date)
##    end_date_def=datetime.datetime(datetime_list_def[-1].year, datetime_list_def[-1].month, datetime_list_def[-1].day)
##
##    ## Prepare for creation of date list
##    date_list_def=[]
##    
##    ## This is done this way at the moment in case there are missing dates, at least every day will still have
##    ## a space allocated for it. 
##    while current_date_def<=end_date_def:
##        date_list_def.append(current_date_def)
##        current_date_def=current_date_def+datetime.timedelta(days=1)
##
##    ## Make a number of unique lists
##    unique_lists=[]
##    for i in range(number_of_columns_def):
##        unique_lists.append([])
##        for j in range(len(date_list_def)):
##            unique_lists[i].append([])
##
##    datetime_list_by_day_def=unique_lists[0]
##                                   
##    data_lists_by_day_def=[]
##    ## For as many columns of data there are
##    for i in range(1,number_of_columns_def):
##        ## Make room for that column of data to be sorted by day
##        data_lists_by_day_def.append(unique_lists[i])
##
##        
##    ## Go through the huge list and put everything where it goes.
##    ## FOR EVERY SINGLE DATA POINT in the original datetime list
##    for i in range(len(datetime_list_def)):
##
##        ## Strip the time off of the datetime in the interval datetime list
##        interval_data_day_def=datetime.datetime(datetime_list_def[i].year,datetime_list_def[i].month,datetime_list_def[i].day)
##
##        ## Then find the index for that day in the date list
##        index_def=date_list_def.index(interval_data_day_def)
##        #print index_def
##
##        datetime_list_by_day_def[index_def].append(datetime_list_def[i])
##
##        for k in range(len(interval_data_def[1:])):
##            data_lists_by_day_def[k][index_def].append(data_lists_def[k][i])
##                                       
##    return_list_def=[]
##
##    for i in range(len(interval_data_def[1:])):
##        return_list_def.append([datetime_list_by_day_def,data_lists_by_day_def[i]])
##
##    return return_list_def



##def get_operating_hours_from_user_old():
##
##    #bucket_specifying_open_or_closed="open"
##    ## I am rewriting this to have error checking and also to be more intuitive
##
##    got_to_end=False
##    acceptable_answers=["open","closed"]
##    while got_to_end==False:
##        
##        bucket_specifying_open_or_closed=raw_input("--Are you specifying a time when the building is open, or when it is closed? >>> ")
##
##        if bucket_specifying_open_or_closed in acceptable_answers:
##            got_to_end=True
##        else:
##            print "--Please input either open or closed"
##
##    bucket_start_day_text="0:00"
##    #bucket_start_time_text="6:00"
##    #bucket_end_time_text="18:00"
##    bucket_end_day_text="23:45"
##
##    bucket_start_time_text=raw_input("--Input start time. No error checking here so be careful. hh:mm >>> ")
##    bucket_end_time_text=raw_input("--Input end time. No error checking here so be careful. hh:mm >>> ")
##
##    bucket_start_day=parser.parse(bucket_start_day_text)
##    bucket_start_time=parser.parse(bucket_start_time_text)
##    bucket_end_time=parser.parse(bucket_end_time_text)
##    bucket_end_day=parser.parse(bucket_end_day_text)
##
##    
##    bucket_current_time=bucket_start_day
##    bucket_open_closed=[]
##
##    while bucket_current_time<=bucket_end_day:
##        
##        if bucket_current_time<bucket_start_time or bucket_current_time>=bucket_end_time:
##            if bucket_specifying_open_or_closed=="open":
##                bucket_open_closed.append(0)
##            else:
##                bucket_open_closed.append(1)
##        else:
##            if bucket_specifying_open_or_closed=="open":
##                bucket_open_closed.append(1)
##            else:
##                bucket_open_closed.append(0)
##                
##        bucket_current_time=bucket_current_time+datetime.timedelta(minutes=15)    
##
##    return bucket_open_closed

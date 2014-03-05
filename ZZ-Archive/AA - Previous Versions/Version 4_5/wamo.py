
import os, time, datetime
import numpy as np, pandas as pd
from marbles import glass as chan
from openpyxl import Workbook
from openpyxl import load_workbook
import wam as wam, wamo as wamo
from dateutil import parser


## Check this shit out!!!!!!

##import pandas as pd
##wb = pd.ExcelFile('DataInput2013.xlsx')
##sheet=wb.parse('Interval Usage')
##timestamps=sheet.DateTimeStamp
##elap=timestamps[len(timestamps)-1]-timestamps[0]
##elec=sheet['Electric(kWh)']
##headings=sheet.columns
##for heading in headings:
##    print sheet[heading][0]
            

class IntervalData(object):

    def __init__(self, pandas_data_frame):

        self.dataframe=pandas_data_frame

        self.datetime_list=pandas_data_frame[pandas_data_frame.columns[0]]
        
        #self.data_list=interval_data_def[1]

        #self.datetime_list_by_day=self.interval2day(interval_data_def[0])

        #self.data_list_by_day=interval_data_by_day_def[1]

        #self.averages_by_day=self.list_of_lists_2_list_of_ave(self.data_list_by_day)

        #self.num_matches=5

        #self.date_list=self.get_date_list(self.datetime_list)

    def get_elapsed_days(self):
        
        return self.datetime_list_by_day[-1][0]-self.datetime_list_by_day[0][0]


    def list_of_lists_2_list_of_ave(self, list_of_lists_def):

        list_of_aves_def=[]
        
        for i in range(len(list_of_lists_def)):
            try:
                daily_ave_def=float(sum(list_of_lists_def[i]))/len(list_of_lists_def[i])
            except:
                daily_ave_def="err"
            list_of_aves_def.append(daily_ave_def)
        return list_of_aves_def

    def get_date_list(self, datetime_list):

        current_date_def=datetime_list[0]
        end_date_def=datetime_list[-1]
        date_list_def=[]
        while current_date_def<=end_date_def:
            date_list_def.append(current_date_def)
            current_date_def=current_date_def+datetime.timedelta(days=1)

        return date_list_def

    def interval2day(interval_data_def):


        number_of_non_date_columns_def=len(interval_data_def[1:])
        
        number_of_columns_def=len(interval_data_def)

        ## The datetime is assumed to be the first list 
        datetime_list_def=interval_data_def[0]

        ## Create space for the lists of data (exclude the date)
        data_lists_def=[]

        ## Now I have a list of at least one other list, but possibly more
        for i in range(1,number_of_columns_def):
            
            data_lists_def.append(interval_data_def[i])


        ## Get the first date (assumed to be the earliest date)
        current_date_def=datetime.datetime(datetime_list_def[0].year, datetime_list_def[0].month, datetime_list_def[0].day)

        ## Get the last date (assumed to be the most recent date)
        end_date_def=datetime.datetime(datetime_list_def[-1].year, datetime_list_def[-1].month, datetime_list_def[-1].day)

        ## Prepare for creation of date list
        date_list_def=[]
        
        ## This is done this way at the moment in case there are missing dates, at least every day will still have
        ## a space allocated for it. 
        while current_date_def<=end_date_def:
            date_list_def.append(current_date_def)
            current_date_def=current_date_def+datetime.timedelta(days=1)

        ## Make a number of unique lists
        unique_lists=[]
        for i in range(number_of_columns_def):
            unique_lists.append([])
            for j in range(len(date_list_def)):
                unique_lists[i].append([])

        datetime_list_by_day_def=unique_lists[0]
                                       
        data_lists_by_day_def=[]
        ## For as many columns of data there are
        for i in range(1,number_of_columns_def):
            ## Make room for that column of data to be sorted by day
            data_lists_by_day_def.append(unique_lists[i])

            
        ## Go through the huge list and put everything where it goes.
        ## FOR EVERY SINGLE DATA POINT in the original datetime list
        for i in range(len(datetime_list_def)):

            ## Strip the time off of the datetime in the interval datetime list
            interval_data_day_def=datetime.datetime(datetime_list_def[i].year,datetime_list_def[i].month,datetime_list_def[i].day)

            ## Then find the index for that day in the date list
            index_def=date_list_def.index(interval_data_day_def)
            #print index_def

            datetime_list_by_day_def[index_def].append(datetime_list_def[i])

            for k in range(len(interval_data_def[1:])):
                data_lists_by_day_def[k][index_def].append(data_lists_def[k][i])
                                           
        return_list_def=[]

        for i in range(len(interval_data_def[1:])):
            return_list_def.append([datetime_list_by_day_def,data_lists_by_day_def[i]])

        return return_list_def


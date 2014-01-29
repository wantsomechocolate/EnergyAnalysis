
import os, time, datetime
import numpy as np, pandas as pd
from marbles import glass as chan
from openpyxl import Workbook
from openpyxl import load_workbook
import wam as wam, wamo as wamo
from dateutil import parser


class MyWorkbook(object):

    def __init__(self, book_name):

        ## Load workbook using the pandas library - so much faster!!!!  
        self.wb = pd.ExcelFile(book_name)

        self.sheet_names=self.wb.sheet_names

        ## This will store all of the sheet objects
        self.sheet_objects=[]
        
        ## For each sheet, go in and get the addresses and actual data for each row and
        ## and column that contain any data. 
        for i in range(len(self.sheet_names)):

            ## This initializes a sheet object, which takes the sheet name
            ## and returns the data in that sheet as a list of lists representing columns.
            self.sheet_objects.append(MySheet(self.wb, self.sheet_names[i]))

        ## This creates as many objects as sheets with the actual data inside (including the headings)
        ## and puts it in a dictionary keyed with the sheet names
        self.work_book_data={}
        self.work_book_data_no_headings={}
        for i in range(len(self.sheet_names)):
            self.work_book_data[self.sheet_names[i]]=self.sheet_objects[i].sheet_data

            no_heading_intermediate=[]
            for k in range(len(self.sheet_objects[i].sheet_data)):
                no_heading_intermediate.append(self.sheet_objects[i].sheet_data[k][1:])

            self.work_book_data_no_headings[self.sheet_names[i]]=no_heading_intermediate
            
    
    def get_num_sheets(self):

        return len(self.sheet_objects)

## A sheet object has all the data from the sheet in it.
## Sheet data range is a bunch of cell addresses, sheet data is the data at those addresses.
class MySheet(object):

    def __init__(self, workbook, sheet_name):

        ## I believe this produces a generator? You can print the data and iterate the data
        ## but it isn't a python list
        self.sheet=workbook.parse(sheet_name)

        ## This values operator puts all the data without headings(:/) into a list of lists
        ## representing rows
        self.sheet_data_by_row=self.sheet.values

        ## Zip it to represent columns instead. 
        self.sheet_data_by_col=zip(*self.sheet_data_by_row)

        self.sheet_data=[]

        ## Here sheet.columns actually only returns a list of strings, one item for each row
        ## aka the text at the top of the column. 
        for i in range(len(list(self.sheet.columns))):
            ## this actually puts the sheet name back into the list as the first entry
            self.sheet_data.append(list(self.sheet_data_by_col[i]))
            ## because downstream of this it expects it that way. I can rework in the future.
            self.sheet_data[i].insert(0,[list(self.sheet.columns)[i]])

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

    def __init__(self, interval_data_def, interval_data_by_day_def):

        self.datetime_list=interval_data_def[0]
        
        self.data_list=interval_data_def[1]

        self.datetime_list_by_day=interval_data_by_day_def[0]

        self.data_list_by_day=interval_data_by_day_def[1]

        self.averages_by_day=self.list_of_lists_2_list_of_ave(self.data_list_by_day)

        self.num_matches=5

        self.date_list=self.get_date_list(self.datetime_list)

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


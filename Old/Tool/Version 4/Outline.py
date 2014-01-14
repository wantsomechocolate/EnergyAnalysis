##I want the program to run in an environment.
##It will start up and ask you what you want to do
##Load a workbook? surething. Get info about that wb, done.
##
##Or should I just abondon this and go with the CSV method........
##
##then I really would need my own class.
##
##If I go the csv route, then I will need to once and for all
##make the program handle multiple columns.
##
##It will be one object with a date_list object, and n data_list
##objects.
##
##the date_list object will have methods to get the date_list, the
##interval date by day, the length of the period etc
##
##The data_list objects will have all the methods needed for both
##usage and weather analysis. 

##The program will use dictionaries
##
##sheet names will be keys while the value corresponding to each sheet
##key will be the another dictionary with the keys being heading names and
##the data being the values.
##
##or should the final value be interval_data objects? or time list objects?
##yeeeaaaaah. That sounds pretty nice.

class MyCSV(object):

    def __init__(self, csv_name):

        fh = open(csv_name)

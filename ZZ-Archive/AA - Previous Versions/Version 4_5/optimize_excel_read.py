## Get to the excel data much more quickly than before.

import pandas as pd
from time import time as time

time1=time()

workbook=pd.ExcelFile("../Sample Input/Data Input.xlsx")
#xl.sheet_names
sheet=workbook.parse("Interval Usage")
sheet_data_by_row=sheet.values
sheet_data_by_col=zip(*sheet_data_by_row)

sheet_data=[]

for i in range(len(list(sheet.columns))):
    
    sheet_data.append(list(sheet_data_by_col[i]))
    sheet_data[i].insert(0,[list(sheet.columns)[i]])


time2=time()

print "That took: "+str(int(time2-time1))+" seconds"

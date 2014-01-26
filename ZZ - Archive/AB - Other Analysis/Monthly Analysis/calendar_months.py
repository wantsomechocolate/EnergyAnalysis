## Utility bill normalization
## Should let user know of gaps, overlaps, etc
## let user set max gap (default 1 because some bills do that)
## user should be able to select either calender months
## or 12 months of equal length
## or 30 day months? although I'm not sure how that last one would work.
## So the idea is to be able to take two dates, and be able to break out how much
## time is in each calender months between the two dates. 
import datetime

def xl2dtobj(xl_date,datemode):
    return (
        datetime.datetime(1899,12,30)
        + datetime.timedelta(days=xl_date + 1462 * datemode)
        )

import numpy as np

##----------The Data------------

start_time=[41429,41396,41368,41339,41308,41277,41247,41213,41184,41152,41123,41093,41062,41032,41003,40971,40942,40911,40879]

start_time=np.array(start_time)

end_time=[41457,41428,41395,41367,41338,41307,41276,41246,41212,41183,41151,41122,41092,41061,41031,41002,40970,40941,40910]

end_time=np.array(end_time)

data=[786324,804826,629150,602236,704658,627496,655446,745308,847280,694370,813930,895260,827200,791762,712524,
      700566,727640,730692,701464]

data=np.array(data)

##-------------End Data----------------

days_elapsed=list((end_time)-(start_time))

average_per_day=data/days_elapsed

#for item in days_elapsed: print item
#for item in average_per_day: print item

start_date_datetime_obj=[]
end_date_datetime_obj=[]

for item in start_time:
    start_date_datetime_obj.append(xl2dtobj(int(item),0))

for item in end_time:
    end_date_datetime_obj.append(xl2dtobj(int(item),0))

array_len=0
if len(start_time)<=len(end_time):
    array_len=len(start_time)
    
else: array_len=len(end_time)

#print array_len

#what is the first item in start date?
first_date = start_date_datetime_obj[len(start_date_datetime_obj)-1]
#what is the last item in end date
last_date = end_date_datetime_obj[0]

total_elapsed_time=last_date-first_date
#print total_elapsed_time

elapsed_time_list=[]

for i in range(array_len):
    elapsed_time=end_date_datetime_obj[i]-start_date_datetime_obj[i]
    elapsed_time_list.append(elapsed_time)

for i in range(len(elapsed_time_list)):
    
    current








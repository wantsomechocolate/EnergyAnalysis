import wam


sample_day=[377.28, 357.12, 354.24, 352.8, 351.36, 354.24, 355.68, 348.48, 348.48, 351.36, 348.48, 349.92, 349.92, 345.6, 351.36, 348.48, 347.04, 348.48, 357.12, 355.68, 347.04, 348.48, 348.48, 352.8, 370.08, 423.36, 488.16, 535.68, 573.12, 603.36, 622.08, 632.16, 650.88, 682.56, 699.84, 722.88, 750.24, 766.08, 783.36, 793.44, 792, 794.88, 804.96, 803.52, 812.16, 820.8, 823.68, 813.6, 807.84, 809.28, 815.04, 815.04, 825.12, 816.48, 813.6, 812.16, 816.48, 820.8, 816.48, 812.16, 815.04, 806.4, 806.4, 815.04, 823.68, 796.32, 770.4, 751.68, 750.24, 744.48, 735.84, 721.44, 702.72, 590.4, 565.92, 547.2, 542.88, 532.8, 518.4, 508.32, 502.56, 493.92, 478.08, 470.88, 463.68, 470.88, 457.92, 455.04, 449.28, 436.32, 427.68, 423.36, 414.72, 403.2, 394.56, 393.12]

num_min_val=10

percent_above=.03

sample_day_k_min_ave=wam.get_ave_of_k_min_values(sample_day,num_min_val)

percent_above_min=(1+percent_above)*sample_day_k_min_ave

percent_below_min=(1-percent_above)*sample_day_k_min_ave


##psuedo code

## the goal is to find a certain number of points that are all above the baseline for a sustained period
## the problem is that the time span must begin near the line, but I want it so sustain a differential after
## a certain point.

## The first point must be above - let's say first hour actually (that's 4 points)

points_that_are_at_least_above_k_min_ave=4

## then I want it to sustain a gap of at least

## let's give up on the step up thing and just code it the normal way first.

thresh=12 ##three hours will designate a start up

count=0

faux_day=[]

for i in range(len(sample_day)):

    if sample_day[i]>percent_above_min:

        count=count+1

    if sample_day[i]<percent_below_min:

        count=0

    faux_day.append(count)

print faux_day


start_time_each_day=['N/A', 5.0, 5.5, 5.0, 3.0, 5.5, 7.0, 9.5, 5.0, 5.75, 5.5, 5.75, 5.5, 7.0, 10.5, 5.0, 5.5, 5.75, 5.0, 5.75, 7.0, 'err', 4.5, 5.75, 5.5, 5.5, 5.75, 6.5, 9.5, 5.0, 5.25, 5.75, 5.5, 5.75, 6.5, 13.0, 5.0, 'err', 4.5, 5.75, 5.75, 6.0, 3.5, 4.75, 5.75, 5.5, 6.0, 5.5, 6.75, 14.0, 4.75, 5.25, 5.5, 5.75, 5.75, 6.5, 10.75, 5.0, 5.75, 5.75, 5.75, 5.75, 7.0, 11.0, 5.0, 5.75, 5.75, 5.75, 5.75, 7.25, 10.5, 5.5, 5.75, 5.75, 5.75, 5.5, 6.25, 11.75, 5.25, 6.0, 5.75, 5.75, 5.75, 6.75, 11.0, 5.5, 5.5, 5.5, 5.75, 5.75, 7.0, 13.5, 5.25, 5.75, 5.75, 5.75, 5.5, 'err', 11.0, 5.25, 5.75, 5.75, 5.75, 5.75, 6.5, 9.0, 5.5, 5.75, 4.5, 4.0, 5.25, 7.0, 13.25, 5.0, 5.75, 5.25, 5.75, 5.25, 7.5, 10.0, 4.75, 5.5, 5.75, 5.5, 5.75, 7.0, 9.75, 5.25, 5.75, 5.75, 5.75, 5.5, 6.5, 10.0, 4.75, 5.25, 5.25, 5.75, 5.75, 7.0, 9.0, 5.0, 5.5, 5.5, 5.5, 5.75, 7.0, 11.0, 5.25, 4.0, 5.25, 5.5, 5.5, 6.0, 9.5, 5.5, 5.5, 5.5, 5.5, 5.5, 7.0, 9.5, 4.25, 5.0, 5.25, 5.5, 5.5, 6.75, 9.0, 5.25, 5.25, 4.0, 4.25, 4.25, 6.5, 9.5, 4.0, 5.5, 5.75, 5.5, 4.0, 'err', 9.0, 4.25, 4.0, 6.0, 4.0, 4.0, 5.75, 7.25, 4.25, 5.5, 5.25, 5.75, 5.5, 7.0, 7.0, 4.0, 4.25, 4.0, 5.5, 5.5, 7.0, 6.5, 4.0, 4.0, 5.5, 5.5, 5.0, 6.0, 9.75, 4.25, 5.5, 5.25, 5.5, 5.5, 6.5, 8.75, 4.0, 5.5, 4.75, 5.5, 5.0, 6.5, 7.75, 4.0, 5.5, 5.5, 5.5, 5.25, 7.0, 8.25, 4.25, 5.5, 5.5, 5.5, 5.25, 6.75, 9.5, 4.25, 4.75, 5.5, 5.5, 5.5, 6.5, 8.75, 5.25, 4.25, 5.75, 5.75, 5.25, 6.75, 6.75, 4.5, 5.75, 5.5, 5.5, 5.25, 6.5, 7.0, 5.25, 5.25, 5.75, 5.75, 5.5, 6.5, 7.0, 5.25, 5.75, 5.5, 5.75, 5.25, 6.25, 8.5, 5.25, 5.75, 5.5, 5.5, 5.5, 6.75, 8.25, 5.25, 6.0, 5.75, 5.75, 5.5, 7.0, 7.25, 5.25, 5.75, 5.75, 5.75, 5.75, 6.5, 7.5, 5.5, 5.5, 5.5, 5.5, 5.5, 6.0, 9.25, 5.25, 6.0, 5.75, 6.0, 5.75, 7.0, 8.75, 5.25, 5.75, 5.75, 4.75, 5.25, 6.75, 8.5, 5.25, 5.5, 5.75, 5.75, 5.75, 7.0, 7.25, 5.0, 5.5, 5.5, 6.0, 6.0, 6.0, 8.75, 5.0, 5.75, 5.5, 5.75, 5.75, 7.0, 9.25, 5.25, 5.75, 5.75, 5.75, 5.75, 7.25, 9.25, 5.25, 5.75, 5.75, 5.75, 5.5, 7.0, 10.0, 5.25, 5.75, 5.75, 5.75, 5.75, 6.75, 12.25, 5.5, 6.0, 5.5, 5.75, 4.75, 7.0, 'N/A', 0.75]


year_of_weeks_by_weekday_start_time=[]
>>> for i in range(53):
	year_of_weeks_by_weekday_start_time.append([])

	
>>> for i in range(len(interval_time_by_day)):
	if interval_time_by_day[i][10].isoweekday()<6:
		year_of_weeks_by_weekday_start_time[interval_time_by_day[i][10].isocalendar()[1]-1].append(start_time_each_day[i])

		
>>> for week in year_of_weeks_by_weekday_start_time:
	print week


>>> doi=start_time_each_day.index(13)+2
>>> p=pl.plot_date(interval_time_by_day[doi],interval_usage_by_day[doi],'-g')
>>> p=pl.plot_date(interval_time_by_day[doi],baseline_by_day[doi],'-r')
>>> xaxisdate=interval_time_by_day[doi][0]
>>> xaxislabel="Year:"+str(xaxisdate.year)+" Month:"+str(xaxisdate.month)+ " Day of month:"+str(xaxisdate.day) + " Day of week:"+str(xaxisdate.isoweekday())
>>> p=pl.xlabel(xaxislabel)
>>> pl.show()



>>> percent_above_baseline=0.05
>>> count=0
>>> thresh=8
>>> start_time=[]
>>> start_time_each_day=[]
>>> for i in range(len(interval_usage_by_day)):

    found_start_time="No"
    start_time=[]
    count=0

    ## for every 15 minute period
    for j in range(len(interval_usage_by_day[i])):
        
        

        ##if the usage during the 15 minutes is greater than a percentage more than the baseline
        if interval_usage_by_day[i][j]>baseline_by_day[i][j]*(1+percent_above_baseline):
            ## increase count
            count=count+1
        else:
            ## otherwise reset count
            count=0

        ## at this point, count could be from 0 to 96 (every value higher than baseline)

        ## if at any point it becomes greater than thresh and it hasn't before today
        if count>=thresh and found_start_time=="No":
            ## say that the start time occured when the increase started
            start_time=float(j-thresh)/4

            ## and say that a start time was found for the day
            found_start_time="Yes"

    if found_start_time=="Yes":
        if start_time<0:
            start_time_each_day.append("err")
        else:
            start_time_each_day.append(start_time)
    else:
        start_time_each_day.append("N/A")

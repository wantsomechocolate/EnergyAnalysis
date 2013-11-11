def interval2day(time_list_def, data_list_def):


    current_date_def=datetime.datetime(time_list_def[0].year, time_list_def[0].month, time_list_def[0].day)
    
    end_date_def=datetime.datetime(time_list_def[-1].year, time_list_def[-1].month, time_list_def[-1].day)
    
    date_list_def=[]
    
    while current_date_def<=end_date_def:
        
        date_list_def.append(current_date_def)
        
        current_date_def=current_date_def+datetime.timedelta(days=1)

    ts_by_day_def=[]
    for i in range(len(date_list_def)):
        ts_by_day_def.append([])
    
    wbt_by_day_def=[]
    for i in range(len(date_list_def)):
        wbt_by_day_def.append([])


    ## Go through the huge list and put everything where it goes.

    for i in range(len(time_list_def)): ## FOR EVERY SINGLE DATA POINT (8000 FOT TEMP, 30000 FOR INTERVAL)

        for j in range(len(date_list_def)): ## FOR EVERY DAY THAT FALLS IN THE RANGE BETWEEN THE OLDEST AND NEWEST DATE IN THE DATE RANGE

            ## STRIP OFF THE TIME COMPONENT FROM THE INTERVAL DATETIME, IF THE DATE MATCHES THE CURRENT DAY THEN ADD, IF NOT MOVE ON!
            interval_data_day_def=datetime.datetime(time_list_def[i].year,time_list_def[i].month,time_list_def[i].day)

            if interval_data_day_def==date_list_def[j]:
                   ts_by_day_def[j].append(time_list_def[i])
                   wbt_by_day_def[j].append(data_list_def[i])
                   

    return_list_def=[ts_by_day_def,wbt_by_day_def]

    return return_list_def

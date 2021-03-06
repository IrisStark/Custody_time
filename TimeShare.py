import calendar
import warnings
warnings.simplefilter(action='ignore')
#from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
import holidays
import pandas as pd
import numpy as np
import datetime
import math
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import calmap
pd.set_option('display.max_rows', 100)


'''This function takes user input for calendar class'''
def user_input_schedule():
    schedule_name = input('Name your schedule')
    whose_this_schedule = input('Mom or Dad?')  #drop down choice
    frequency = input('Weekly or alternative weeks?') #drop down choice
    start_date = input('Enter start date of the schedule:') #show calendar
    time_schedule_starts = input('Enter time of the beginning of the schedule') #show scroll time window
    end_date = input('Enter end date of the schedule or press blank if there is no end date:') #show calendar
    time_schedule_ends = input('Enter time of the end of the schedule or press blank if there is no end time') #show scroll time window
    days = input(f'Choose days with {whose_this_schedule}:') #show buttons with days of the week
    start_time = input('Enter exchange time on the fist day') #show scroll time window
    end_time = input('Enter exchange time on the last day') #show scroll time window
    return schedule_name, whose_this_schedule, frequency, start_date, when_schedule_starts, end_date, \
           when_schedule_ends, days, start_time, end_time

class CustodyHolidays(holidays.HolidayBase):        
    def _populate(self, year):
        c = calendar.Calendar(firstweekday=calendar.SUNDAY)
        # Populate the holiday list with the default US holidays
        holidays.UnitedStates._populate(self, year)
        #add mother's day
        monthcal = c.monthdatescalendar(year,5)
        needed_date = [day for week in monthcal for day in week if \
                        day.weekday() == 6 and \
                        day.month == 5][1]
        self[datetime.date(year, needed_date.month, needed_date.day)] = "Mother's day"
        #add father's day
        monthcal = c.monthdatescalendar(year,6)
        needed_date = [day for week in monthcal for day in week if \
                        day.weekday() == 6 and \
                        day.month == 6][2]
        self[datetime.date(year, needed_date.month, needed_date.day)] = "Father's day"
        #add Halloween
        self[datetime.date(year, 10, 31)] = "Halloween"  
 
        #add easter
        a = year % 19
        b = year % 4
        c = year % 7
        d = ((19 * a) + 24) % 30
        e = ((2 * b) + (4 * c) + (6 * d) + 5) % 7
        date = 22+d+e
        if 22 <= date <= 31:
            needed_date = datetime.date(year, 3, date)


        elif  32 <= date <= 56: 
            needed_date = datetime.date(year, 4, date-31)
        self[datetime.date(year, needed_date.month, needed_date.day)] = "Easter"
        
def start_end_dates(df, month_of_year_starts, week_of_month_starts, day_of_week_starts,  \
                    month_of_year_ends, week_of_month_ends, day_of_week_ends):
        c = calendar.Calendar(firstweekday=calendar.SUNDAY)
        years = df['date'].loc[df['date'].dt.month==month_of_year_starts].dt.year.unique()  
        start_dates = []
        end_dates = []
        for year in years:
            monthcal = c.monthdatescalendar(year,month_of_year_starts)      
            start_date = [day for week in monthcal for day in week if \
                            day.weekday() == day_of_week_starts and \
                            day.month == month_of_year_starts][week_of_month_starts]
            monthcal = c.monthdatescalendar(year,month_of_year_ends)
            end_date = [day for week in monthcal for day in week if \
                            day.weekday() == day_of_week_ends and \
                            day.month == month_of_year_ends][week_of_month_ends]
            start_date = pd.to_datetime(start_date)+time_schedule_starts
            end_date = pd.to_datetime(end_date)+time_schedule_ends
            if end_date < start_date:
                end_date = end_date + datetime.timedelta(days=7)
            start_dates.append(start_date)
            end_dates.append(end_date)
        return start_dates, end_dates
    
def right_label(df, start_date, end_date, time_schedule_starts, time_schedule_ends, is_odd, whose_this_schedule):
    other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
    if is_odd == True and start_date.year%2!=0:
        df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = whose_this_schedule
    elif is_odd == True and start_date.year%2==0:
        df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = other_party
    elif is_odd == False and start_date.year%2==0:
        df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = whose_this_schedule
    else:
        df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = other_party
    return df

def right_time(df, start_date, end_date, time_schedule_starts, time_schedule_ends, whose_this_schedule):  

    df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'start_date'] =  pd.to_datetime(df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()),'start_date'].dt.date)+time_schedule_starts
    
    df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()) & (df['label']==whose_this_schedule), 'end_date'] = pd.to_datetime(df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date())& (df['label']==whose_this_schedule),'end_date'].dt.date)+time_schedule_starts
    
    df.loc[(df['end_date'].dt.date==end_date.date())&(df['label']==whose_this_schedule),'end_date'] = end_date.replace(hour=0,minute=0)+time_schedule_ends
    df.loc[(df['start_date'].dt.date==end_date.date())&(df['label']!=whose_this_schedule),'start_date'] = end_date.replace(hour=0,minute=0)+time_schedule_ends
    
    df.loc[(df['end_date'].dt.date==start_date.date()),'end_date'] = pd.to_datetime(df.loc[(df['end_date'].dt.date==start_date.date()),'end_date'].dt.date)+time_schedule_starts

    df['time_diff_hours'] = (df['end_date'] - df['start_date']).dt.total_seconds()/3600

    return df 

'''this class is being used to populate pandas data frame with dates and assign them to a person
according to the schedule
Input:
start date of the schedule (datetime.date)
end date of the schedule (datetime.date) or '' if schedule is endless
shedule name - name of the schedule like holidays, normal schedule etc
days - list of interger days Monday=0, Sunday=6 (can be equal to 1!!!!) from exchange time to exchange time
start_month_date, end_month_date - tuple(month,day) year is unknown
Creates:
pandas frame with columns date, day of week, time_exchange,time_spent_a_day, label 0/1 (1 for person who creates schedule) (don't care about 3d party option here),
is_clash_of_time'''
class Calendar():
    def __init__(self):
        pass

    '''function to create schedule. Outputs data frame
    is_same_every_year schould be equal to False if dates of beginning and end of schedule are different every year
    '''
    def schedule(self,schedule_name, frequency, time_schedule_starts, time_schedule_ends, whose_this_schedule,\
                days, start_date=None, end_date=None, is_same_every_year=True, df=None, month_of_year_starts=None, \
                 week_of_month_starts=None, day_of_week_starts=None,  month_of_year_ends=None, \
                 week_of_month_ends=None, day_of_week_ends=None, start_month_date=None, end_month_date=None):
        if start_date != None:
            start_dates = [start_date]
        elif month_of_year_starts != None:
            start_dates, _ = start_end_dates(df, month_of_year_starts, week_of_month_starts, day_of_week_starts,  \
                month_of_year_ends, week_of_month_ends, day_of_week_ends)
        else:
            years = df.date.dt.year.unique()
            start_dates = []
            end_dates = []
            for year in years:
                candidate_start = datetime.date(year, date_starts[0], date_starts[1])
                if pd.to_datetime(candidate_start) in sh_1.date.dt.date.to_list():
                    start_date = pd.to_datetime(candidate_start)+time_schedule_starts
                    candidate_end = datetime.date(year, date_ends[0], date_ends[1])
                
                if pd.to_datetime(candidate_start) in sh_1.date.dt.date.to_list():
                    start_date = pd.to_datetime(candidate_start)+time_schedule_starts
                if pd.to_datetime(candidate_end) in sh_1.date.dt.date.to_list():
                    end_date = pd.to_datetime(candidate_end)+time_schedule_ends
                start_dates.append(start_date)
                end_dates.append(end_date)
                    
        if end_date != None:
            end_dates = [end_date]
        if end_date == None and day_of_week_ends == None:
            end_dates=[start_date+datetime.timedelta(days=365*36)]
        elif month_of_year_ends != None:
            _, end_dates = start_end_dates(df, month_of_year_starts, week_of_month_starts, day_of_week_starts,  \
                month_of_year_ends, week_of_month_ends, day_of_week_ends)

    #___
        if whose_this_schedule != 'Dad' and whose_this_schedule !='Mom':
            print('Wrong whose_this_schedule input. Should be "Dad" or "Mom"')
   #____         
            
        for start_date, end_date in zip(start_dates, end_dates):    
            start_date = pd.to_datetime(start_date)           
            end_date = pd.to_datetime(end_date)
            other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
            number_of_weeks = math.ceil((end_date-start_date).days/7)
            #for weekly and alternative weeks
            if frequency=='weekly':
                days_in_round = 7
            else:
                days_in_round = 14

            #TODO account if schedule starts on different day, then custody time begins
            if len(days)==7:
                labels = [whose_this_schedule]*7
                labels.extend([other_party]*7)
            else:
                labels = [whose_this_schedule]*(len(days)-1)
                labels.extend([other_party]*(days_in_round-len(days)+1))


            if df is None:
                df = self.add_rows(end_date, start_date, labels, time_schedule_ends, other_party, \
                                        days_in_round, time_schedule_starts, schedule_name)
            else:
                keep_df = df[(df['date']<start_date) | (df['date']>end_date)]
                changed_df = self.add_rows(end_date, start_date, labels, time_schedule_ends, other_party, \
                                           days_in_round, time_schedule_starts, schedule_name)
                df = pd.concat([keep_df,changed_df])
                df=df.sort_values(by=['date'])
            
        
    #TODO 
    #add 2-2-3 schedule or schedule with different days in alternative weeks, 2-2-5-5, Two weeks each,
    #X days each, 3-4-4-3
        df['shedule_names_clash']= None
        df['schedule_clash'] = False
        df.drop_duplicates(inplace=True, subset=['label','start_date','end_date','time_diff_hours'],keep='last')
        df.reset_index(inplace=True, drop=True)
        return df
    
    def add_rows(self, end_date, start_date, labels, time_schedule_ends, other_party, days_in_round, \
                 time_schedule_starts,schedule_name):
        df = pd.DataFrame(columns=['date','label'])
        while start_date < end_date + datetime.timedelta(days=1):   
            week_dates = pd.date_range(start_date, freq='1D', periods=len(labels)).tolist()
            week_dates = pd.to_datetime(week_dates)       
            week_df = pd.DataFrame(list(zip(week_dates, labels)),columns=['date','label'])
            df = df.append(week_df,ignore_index=True)
            start_date = week_dates[-1] + datetime.timedelta(days=1)
        df['date'] = df.apply(lambda x: x['date'].replace(hour=0,minute=0)+time_schedule_starts \
                        if x['label']!=other_party else x['date'].replace(hour=0,minute=0)+time_schedule_ends, axis=1)

        df['start_date'] = df['date']
        df['end_date'] = df['date'].shift(-1)
        df['time_diff_hours'] = (df['end_date'] - df['start_date']).dt.total_seconds()/3600
        df.drop(df[df['date']>end_date].index,inplace=True)
        df['schedule_name'] = schedule_name
        df['is_special']=False
        return df
    
    #dates should be a list of dates in pd.to_datetime format each. Only for one person. Done for every year separately.
    def special_schedule(self,df,dates,whose_this_schedule,schedule_name,time_schedule_ends,time_schedule_starts):
        other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
      
        df['start_date'] = df['date'].replace(hour=0,minute=0)+time_schedule_starts
        #it will make most of the dates 24 hours
        df['end_date'] = df['date'].replace(hour=0,minute=0)+time_schedule_starts
        #it will change the last row's end time to the right one
        df['end_date'].iloc[-1] = df['end_date'].iloc[-1].replace(hour=0,minute=0)+time_schedule_ends
        df['time_diff_hours'] = (df['end_date'] - df['start_date']).dt.total_seconds()/3600
        df.loc[df[df['date'].isin(dates)],'label'] = whose_this_schedule
        
        #check for special schedule clashes
        dates_check = df['date'][(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date())]
        special_dates = df['date'][df['is_special']==True]
        df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates)),'schedule_clash'] = True
        df.loc[df['date'].isin(dates),'is_special'] = True
        df.loc[df[self.df['date'].isin(dates)],'schedule_name'] = schedule_name
        shedule_names = df['shedule_names_clash'][(df['date'].isin(special_dates))&(df['date'].isin(dates))].unique()
        if len(shedule_names)>1:
            shedule_names_clash = str(df['schedule_name'][(df['date'].isin(special_dates))&(df['date'].isin(dates))].unique())
        else:
            shedule_names_clash = shedule_names
        df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates)),'schedule_clash_names'] = shedule_names_clash
        df.drop_duplicates(inplace=True, subset=['label','start_date','end_date','time_diff_hours'],keep='last')
        df.reset_index(inplace=True, drop=True)
        return df
    
    #'Martin Luther King Jr. Day', 'Memorial Day', 'Labor Day'
    #day_of_week_ends - interger 0 -  Monday, 6 - Sunday
    def monday_holiday(self, holiday, day_of_week_ends, time_schedule_ends, df):
        us_holidays = holidays.US(years=list(df['date'].dt.year.unique()))
        dates = pd.to_datetime(us_holidays.get_named(holiday))
        for date in dates:
            if date in df.date.dt.date.unique():
                previous_day = date - datetime.timedelta(days=1)
                last_day = date + datetime.timedelta(days=day_of_week_ends)
                whose_this_schedule = str(df['label'][(df['end_date']>=previous_day) & (df['end_date']<=date)].unique()[0])

                df.loc[(df['end_date']>=previous_day) & (df['end_date']<=last_day), 'label'] = whose_this_schedule
                dates = df['date'][(df['end_date']>=previous_day) & (df['end_date']<=last_day)]

                #My case
                #______________________________________________________________________________________
                '''if exchange time is 8am Tuesday, but his schedule ends on Wednesday 8am it does not make much sense
                for me to pick up kids on Tuesday, cause in this case, I supposed to give him kids on my Monday holidays
                on Tuesday. Probably it could be a case for custodial/not custodial parent.
                Grey area. 

                When both blocks below are commented out - nobody picks up kids on Tuesday

                If both of us pick them up on Tuesday uncomment lines below'''
        #         date_first_day_other_person_schedule = df['date'][(df['start_date'].dt.date >= last_day.date()) & (df['label']!=whose_this_schedule)].iloc[0]
        #         label_other_person = df['label'][(df['start_date'].dt.date >= last_day.date()) & (df['label']!=whose_this_schedule)].iloc[0]
        #         df.loc[(df['start_date'].dt.date>=last_day.date()) & (df['end_date'].dt.date<=date_first_day_other_person_schedule.date()), 'label'] = label_other_person
                '''If only I pick them up on Tuesday uncomment these lines below'''
        #         date_first_day_other_person_schedule = df['date'][(df['start_date'].dt.date >= last_day.date()) & (df['label']!=whose_this_schedule)].iloc[0]
        #         label_other_person = df['label'][(df['start_date'].dt.date >= last_day.date()) & (df['label']!=whose_this_schedule)].iloc[0]
        #         if label_other_person=='Mom':
        #             df.loc[(df['start_date'].dt.date>=last_day.date()) & (df['end_date'].dt.date<=date_first_day_other_person_schedule.date()), 'label'] = label_other_person
            #__________________________________________________________________________________
                #check for special schedule clashes

                dates_check = df['date'][(df['start_date'].dt.date>=start_date) & (df['end_date'].dt.date<=end_date)]
                special_dates = df['date'][df['is_special']==True]
                df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates)),'schedule_clash'] = True
                df.loc[df['date'].isin(dates),'is_special'] = True
                df.loc[df['date'].isin(dates),'schedule_name'] = holiday
                shedule_names = df['shedule_names_clash'][(df['date'].isin(special_dates))&(df['date'].isin(dates))].unique()
                shedule_names_clash = list(shedule_names)
                if len(shedule_names)>1:
                    shedule_names_clash = df['schedule_name'][(df['date'].isin(special_dates))&(df['date'].isin(dates_check))].unique()
                    df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates)),'schedule_clash_names'] = shedule_names_clash
        df.drop_duplicates(inplace=True, subset=['label','start_date','end_date','time_diff_hours'],keep='last')
        df.reset_index(inplace=True, drop=True)
        return df
    
    #when the schedule starts and ends depends on days before and after the holiday
    #days_before_holiday_starts - count days from schedule start to holiday
    #is_changing if holiday alternates odd/even years
    #is_odd - True or False - if whose_this_schedule has custody in odd year it should be True, for even years - False
    def custody_holidays(self, holiday, days_before_holiday_starts, time_schedule_starts, days_after_holiday_ends,\
                         time_schedule_ends, whose_this_schedule, df, is_changing=False,is_odd=None):
        holiday_calendar = CustodyHolidays(years=list(df['date'].dt.year.unique()))
        dates = holiday_calendar.get_named(holiday)
        #there are 2 days in calendar for each of these days
        if holiday == "Christmas":
            years = [d.year for d in dates]
            dates = [datetime.datetime(year,12,24).date() for year in set(years)]
        if holiday == "New Year":
            years = [d.year for d in dates]
            dates = [datetime.datetime(year,12,31).date() for year in set(years)]
        for date in dates:
            if date in df.date.dt.date.unique():
                start_date = pd.to_datetime(date - datetime.timedelta(days=days_before_holiday_starts))+time_schedule_starts
                end_date = pd.to_datetime(date + datetime.timedelta(days=days_after_holiday_ends))+time_schedule_ends
                if is_changing==True:
                    df = right_label(df, start_date, end_date, time_schedule_starts, time_schedule_ends, is_odd, whose_this_schedule)
                else:
                    df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = whose_this_schedule

                df = right_time(df, start_date, end_date, time_schedule_starts, time_schedule_ends, whose_this_schedule)
                dates_check = df['date'][(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date())]

                #check for special schedule clashes
                special_dates = df['date'][df['is_special']==True]
                df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates_check)),'schedule_clash'] = True
                df.loc[df['date'].isin(dates_check),'is_special'] = True
                df.loc[df['date'].isin(dates_check),'schedule_name'] = holiday
                shedule_names = df['shedule_names_clash'][(df['date'].isin(special_dates))&(df['date'].isin(dates_check))].unique()
                shedule_names_clash = list(shedule_names)
                if len(shedule_names)>1:
                    shedule_names_clash = str(df['schedule_name'][(df['date'].isin(special_dates))&(df['date'].isin(dates_check))].unique())

                    df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates_check)),'schedule_clash_names'] = shedule_names_clash
        df.drop_duplicates(inplace=True, subset=['label','start_date','end_date','time_diff_hours'],keep='last')
        df.reset_index(inplace=True, drop=True)
        return df

    #for school breaks kind of schedules. When it's one person, who has kids at that time of schedule. No changes.
    #But it can be different person each year for this period.
    #when we know particular day when it starts (3d monday of second week of febraury or July 3d)
    #week_of_month_ends or week_of_month_ends - interger 0 to 4
    #day_of_week_starts - interger from 0 Monday to 6 Sunday
    #is_special - boolean. If this schedule overwrites regular schedule
    #date_starts, date_ends - month and day (tuple)
    def every_year_changed_schedule(self,  time_schedule_starts, time_schedule_ends, df, whose_this_schedule, \
                                    schedule_name, month_of_year_starts=None, week_of_month_starts=None, \
                                    day_of_week_starts=None,  month_of_year_ends=None, week_of_month_ends=None, \
                                    day_of_week_ends=None, date_starts=None, date_ends=None,  is_changing=False,\
                                    is_odd=None, is_special=False):
        other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
        start_dates = []
        end_dates = []
        if date_starts is not None and date_ends is not None:
            years = df.date.dt.year.unique()
            for year in years:
                candidate_start = datetime.date(year, date_starts[0], date_starts[1])
                
                candidate_end = datetime.date(year, date_ends[0], date_ends[1])
                
                if pd.to_datetime(candidate_start) in df.date.dt.date.to_list():
                    start_date = pd.to_datetime(candidate_start)+time_schedule_starts
                    start_dates.append(start_date)
                if pd.to_datetime(candidate_end) in df.date.dt.date.to_list():
                    end_date = pd.to_datetime(candidate_end)+time_schedule_ends
                    end_dates.append(end_date)

        else:
            start_dates, end_dates = start_end_dates(df, month_of_year_starts, week_of_month_starts, day_of_week_starts,  \
                        month_of_year_ends, week_of_month_ends, day_of_week_ends)

            
        for start_date, end_date in zip(start_dates, end_dates):
            if is_changing==True:
                df = right_label(df, start_date, end_date, time_schedule_starts, time_schedule_ends, is_odd, whose_this_schedule)

            else:
                df.loc[(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date()), 'label'] = whose_this_schedule

            df = right_time(df, start_date, end_date, time_schedule_starts, time_schedule_ends, whose_this_schedule)

            if is_special==True:
                #check for special schedule clashes
                dates_check = df['date'][(df['start_date'].dt.date>=start_date.date()) & (df['end_date'].dt.date<=end_date.date())]
                special_dates = df['date'][df['is_special']==True]
                df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates_check)),'schedule_clash'] = True
                df.loc[df['date'].isin(dates_check),'is_special'] = True
                df.loc[df['date'].isin(dates_check),'schedule_name'] = holiday
                shedule_names = df['shedule_names_clash'][(df['date'].isin(special_dates))&(df['date'].isin(dates_check))].unique()
                shedule_names_clash = list(shedule_names)
                if len(shedule_names)>1:
                    shedule_names_clash = str(df['schedule_name'][(df['date'].isin(special_dates))&(df['date'].isin(dates_check))].unique())
                    df.loc[(df['date'].isin(special_dates))&(df['date'].isin(dates_check)),'schedule_clash_names'] = shedule_names_clash


            df.loc[df['date'].between(start_date,end_date),'schedule_name'] = schedule_name
        df.drop_duplicates(inplace=True, subset=['label','start_date','end_date','time_diff_hours'],keep='last')   
        df.reset_index(inplace=True, drop=True)
        return df
    
    def bug_fix(self,df):
        df['end_date'] = df['start_date'].shift(-1)
        df['time_diff_hours'] = (df['end_date'] - df['start_date']).dt.total_seconds()/3600
        return df
    

       
        
def percentage_with_parent(parent):
    return None

start_date = datetime.date(2022, 6, 3)
time_schedule_starts = pd.to_timedelta('20:00:00')
end_date = datetime.date(2022, 7, 8)
time_schedule_ends = pd.to_timedelta('18:00:00')
days=[4,5,6,0,1,2,3,4]
days = [4,5]
#days = [4,5,6]

sdt = datetime.datetime(2021, 10, 1)
edt = datetime.datetime(2025, 12, 31)
# cal = calendar()
# dt = cal.holidays(start=sdt, end=edt)
# print(dt)
#my calendar 2022

c = Calendar()
#school schedule
start_date = datetime.date(2021, 10, 1)
time_schedule_starts = pd.to_timedelta('18:00:00')
time_schedule_ends = pd.to_timedelta('08:00:00')
sh_1=None
sh_1=c.schedule(schedule_name='school time', whose_this_schedule='Dad', frequency='a', \
                 time_schedule_starts=time_schedule_starts, days=[4,5,6,0,1,2],start_date=sdt,\
           time_schedule_ends=time_schedule_ends,end_date=edt)

time_schedule_ends = pd.to_timedelta('18:00:00')
time_schedule_starts = pd.to_timedelta('18:00:00')
sh_1 = c.schedule(df=sh_1,frequency='a', month_of_year_starts=6, #month_of_year_starts=7
                 week_of_month_starts=1, day_of_week_starts=4,  month_of_year_ends=8, #week_of_month_starts=2
                 week_of_month_ends=0, day_of_week_ends=4, time_schedule_ends=time_schedule_ends,
                  time_schedule_starts=time_schedule_starts,
                     days=[4,5,6,0,1,2,3,4],  schedule_name='summer school break',whose_this_schedule='Dad')

monday_holidays = ['Martin Luther King Jr. Day', "Washington's Birthday", "Memorial Day", 'Labor Day']

time_schedule_ends = pd.to_timedelta('10:00:00')
for holiday in monday_holidays:
    sh_1 = c.monday_holiday(df=sh_1, holiday=holiday, day_of_week_ends=1, \
                                    time_schedule_ends=time_schedule_ends,)
    
sh_1 = c.custody_holidays(df=sh_1, holiday = "Mother's day", days_before_holiday_starts=2,\
                                      time_schedule_starts=pd.to_timedelta('18:00:00'), days_after_holiday_ends=1,\
                             time_schedule_ends=pd.to_timedelta('8:00:00'),whose_this_schedule="Mom")
sh_1 = c.custody_holidays(df=sh_1, holiday = "Father's day", days_before_holiday_starts=2,\
                                      time_schedule_starts=pd.to_timedelta('18:00:00'), days_after_holiday_ends=1,\
                             time_schedule_ends=pd.to_timedelta('8:00:00'),whose_this_schedule="Dad")
sh_1 = c.every_year_changed_schedule(df=sh_1, time_schedule_starts=pd.to_timedelta('08:00:00'), \
                          time_schedule_ends=pd.to_timedelta('18:00:00'), whose_this_schedule='Mom', \
                                    schedule_name='Febraury break', month_of_year_starts=2, week_of_month_starts=2, \
                                    day_of_week_starts=0,  month_of_year_ends=2, week_of_month_ends=2, \
                                    day_of_week_ends=4, is_changing=True,is_odd=False, is_special=True)
sh_1 = c.every_year_changed_schedule(df=sh_1, time_schedule_starts=pd.to_timedelta('08:00:00'), \
                          time_schedule_ends=pd.to_timedelta('18:00:00'), whose_this_schedule='Mom', \
                                    schedule_name='Spring break', month_of_year_starts=4, week_of_month_starts=0, \
                                    day_of_week_starts=0,  month_of_year_ends=4, week_of_month_ends=0, \
                                    day_of_week_ends=4, is_changing=True,is_odd=True, is_special=True)
sh_1 = c.every_year_changed_schedule(df=sh_1, time_schedule_starts=pd.to_timedelta('18:00:00'), \
                          time_schedule_ends=pd.to_timedelta('08:00:00'), whose_this_schedule='Mom', \
                                    schedule_name='4th July', date_starts=(7,3), date_ends=(7,6),\
                                     is_changing=True,is_odd=False, is_special=True)

sh_1 = c.custody_holidays(df=sh_1, time_schedule_starts=pd.to_timedelta('18:00:00'), \
                          time_schedule_ends=pd.to_timedelta('08:00:00'), whose_this_schedule='Mom', \
                                    holiday='Thanksgiving', days_before_holiday_starts=1, days_after_holiday_ends=4,\
                                     is_changing=True,is_odd=False)

sh_1 = c.custody_holidays(holiday='Christmas', days_before_holiday_starts=1,time_schedule_starts=pd.to_timedelta('18:00:00'), \
                          days_after_holiday_ends=2, time_schedule_ends=pd.to_timedelta('08:00:00'), whose_this_schedule="Mom", \
                          df=sh_1, is_changing=True,is_odd=True)

sh_1 = c.custody_holidays(holiday="New Year", days_before_holiday_starts=1,time_schedule_starts=pd.to_timedelta('18:00:00'), \
                          days_after_holiday_ends=2, time_schedule_ends=pd.to_timedelta('08:00:00'), whose_this_schedule="Mom", \
                          df=sh_1, is_changing=True,is_odd=False)

sh_1 = c.bug_fix(sh_1)





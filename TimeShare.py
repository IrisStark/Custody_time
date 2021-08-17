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

'''this class is being used to populate pandas data frame with dates and assign them to a person
according to the schedule
Input:
start date of the schedule (datetime.date)
end date of the schedule (datetime.date) or '' if schedule is endless
shedule name - name of the schedule like holidays, normal schedule etc
days - list of interger days Monday=0, Sunday=6 (can be equal to 1!!!!)
Creates:
pandas frame with columns date, day of week, time_exchange,time_spent_a_day, label 0/1 (1 for person who creates schedule) (don't care about 3d party option here),
is_clash_of_time'''
class Calendar():
    def __init__(self, df=None):
        self.df = df

    '''function to create schedule. Outputs data frame
    is_same_every_year schould be equal to False if dates of beginning and end of schedule are different every year
    '''
    def schedule(self,schedule_name, frequency, time_schedule_starts, time_schedule_ends, whose_this_schedule,\
                days, start_date, end_date=start_date+datetime.timedelta(days=365), is_same_every_year=True):
        
        #To delete after user input built
    #___
        if whose_this_schedule != 'Dad' or whose_this_schedule!='Mom':
            print('Wrong whose_this_schedule input. Should be "Dad" or "Mom"')
   #____         
            
            
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
        
        #updating existing schedule  
        if self.df is not None:
            self.df.loc[(self.df['year_dates']>=start_date) & (self.df['year_dates']<=end_date),'label']= other_party
        #creating first schedule  
        else:
            self.df = pd.DataFrame({'year_dates':pd.date_range(start_date, end_date, freq='1D')})
            self.df['weekdays'] = self.df['year_dates'].dt.weekday
            self.df['week_of_year'] = self.df['year_dates'].dt.week
            self.df['label'] = other_party 
            self.df['is_special'] = False
        
        self.df.loc[(self.df['year_dates']>=start_date) & (self.df['year_dates']<=end_date),'schedule_name'] = schedule_name

        if frequency=='weekly':
            weekly_df = self.add_rows(self.df[(self.df['year_dates']>=start_date) & (self.df['year_dates']<=end_date)], \
                                      time_schedule_starts, time_schedule_ends, days,whose_this_schedule, other_party)
            self.df = pd.concat([weekly_df, self.df[self.df['year_dates']<start_date], self.df[self.df['year_dates']>end_date]])
       
    
    #TODO 
    #add 2-2-3 schedule or schedule with different days in alternative weeks, 2-2-5-5, Two weeks each,
    #X days each, 3-4-4-3
    
    
        else:
            even_odd_week = 1 if self.df['week_of_year'].loc[0]%2==0 else 0
            #if person's schedule starts even week, other person's schedule shall start in odd week
            alternative_df = self.add_rows(self.df[(self.df['week_of_year']%2==even_odd_week) &\
                                                  (self.df['year_dates']>=start_date) & (self.df['year_dates']<=end_date)], time_schedule_starts, \
                                           time_schedule_ends, days,whose_this_schedule, other_party)
            self.df = pd.concat([alternative_df,self.df[(self.df['week_of_year']%2!=even_odd_week) &
                                                       (self.df['year_dates']>=start_date) & (self.df['year_dates']<=end_date)],\
                                self.df[self.df['year_dates']<start_date], self.df[self.df['year_dates']>end_date]])
        self.df=self.df.sort_values(by=['year_dates'])
        self.df=self.df.reset_index(drop=True)

        #self.df['time_diff_minutes'] = (self.df['year_dates'] - self.df['year_dates'].shift(1)).shift(-1).dt.total_seconds()/60
        self.df['time_diff_hours'] = (self.df['year_dates'] - self.df['year_dates'].shift(1)).shift(-1).dt.total_seconds()/3600

        self.df = self.df.sort_index()
        return self.df
    
    def add_rows(self, df, time_schedule_starts, time_schedule_ends, days, whose_this_schedule, other_party):
        start_df = df[df['weekdays']==days[0]]
        start_df['year_dates'] = start_df['year_dates']+time_schedule_starts
        start_df['label'] = whose_this_schedule
        df['label'].loc[df['weekdays'].isin(days[1:])] = whose_this_schedule
        end_df = df[df['weekdays']==days[-1]]
        end_df['year_dates'] = end_df['year_dates']+time_schedule_ends
        end_df['label'] = other_party
        df = pd.concat([start_df,end_df,df])
        return df
    #dates should be a list of dates in pd.to_datetime format each
    def special_schedule(self,dates,whose_this_schedule):
        
        self.df.loc[self.df['year_dates'].isin(dates),'is_special'] = True
        #self.df.loc[self.df[(self.df['year_dates'].isin(dates) &  )],'label'] = whose_this_schedule
        return self.df
        
    def holiday_schedule(self):
        self.df['is_special'] = True
        other_party = 'Mom' if whose_this_schedule == 'Dad' else 'Dad'
        return self.df
        


       

start_date = datetime.date(2021, 8, 8)
time_schedule_ends = pd.to_timedelta('20:00:00')
time_schedule_starts = pd.to_timedelta('12:00:00')#pd.to_datetime('16:30',format= '%H:%M' ).hour
c = Calendar()

sh_1=c.schedule(schedule_name='first', whose_this_schedule='Dad', frequency='a', \
                 time_schedule_starts=time_schedule_starts, days=[3],start_date=start_date,\
           time_schedule_ends=time_schedule_ends)
print(sh_1.head(n=20))
t = sh_1.set_index('year_dates')
t['plot_label']=0
t.loc[t['label']=='Dad', 'plot_label'] = 1
figure(figsize=(15, 20), dpi=80)
calmap.yearplot(t['plot_label'],cmap='spring')

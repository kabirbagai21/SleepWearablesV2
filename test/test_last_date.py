import pandas as pd
import numpy as np
import datetime 

FILE_OUTPUT_STRING = '{aws_path}/{study_name}/{participant_id}/{data_name}.csv'
STUDY_START_DATE = datetime.datetime.strptime('2022-05-12', '%Y-%m-%d')
AWS_PATH = '/home/ec2-user/FitbitTest/'


def last_date_in_file(df, start_date):
    dates = np.asarray(df['Date'])
    datetime_lst = []
    for d in dates:
        datetime_lst.append(d)
    datetime_lst.sort()
    print(datetime_lst)
    try:
        last_date = datetime.datetime.strptime(datetime_lst[-1], '%Y-%m-%d')
    except:
        last_date = start_date
    return last_date


    

def get_last_entry_date(user_email, study_name, start_date):
    '''
    Finds the last entry date for a user to update file
    If no file exists, uses the study start date as the first date to query
    '''
    

    try:
        df1 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='sleep'))
        date1 = last_date_in_file(df1, start_date)
        df2 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='activity'))
        date2 = last_date_in_file(df1, start_date)
        df3 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='heart'))
        date3 = last_date_in_file(df3, start_date)
    except:
        return start_date

    dates = [date1, date2, date3]
    dates.sort()
    return dates[-1]

study_name = 'test'
emails = ['tim@radiclescience.com', 'phpinfo', 'clarissapauli@gmail.com' ,'login.jsp', 'kbagai@ucsd.edu']


for e in emails:
    last_date =  get_last_entry_date(e, study_name, STUDY_START_DATE)
    print(e, last_date)


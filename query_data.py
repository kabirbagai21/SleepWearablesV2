import fitbit
import website.gather_keys_oauth2 as Oauth2
import pandas as pd 
import datetime
from importlib import reload
import numpy as np
import website.DataLoader as DataLoader
import os
import logging
import requests

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

STUDY_START_DATE = datetime.datetime.strptime('2022-05-12', '%Y-%m-%d') #)datetime.datetime.now()# - datetime.timedelta(days=3)
AWS_PATH = '/home/ec2-user/FitbitTest/'
FILE_OUTPUT_STRING = '{aws_path}/{study_name}/{participant_id}/{data_name}.csv'

#userList = [{'user_email': 'tim@radiclescience.com', 'auth_token': 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhCTVAiLCJzdWIiOiI5WENHSEgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNjUyMTUxNjI3LCJpYXQiOjE2NTIxMjI4Mjd9.oJmiouJ8WN2g_pLOkKuAr8c6XHvBkNr1su7mtxBe7Ec', 'refresh_token': '7428648c2ea45cc1fdb7bccb0abcdabae622261e0a580f33262e67710cbff3ba'}]
#clientID = "238BMP"
#clientSecret = "9fc1aafb884bce948bd812995b2fd985"

def refreshAccessToken(refreshToken):
    BodyText = {'grant_type' : 'refresh_token', 'refresh_token' : refreshToken}

    headers = {'Authorization': 'Basic ' + encodedID_Secret,
        'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        log.info('Sending post request for refresh token')
        req = requests.post(TokenURL, params=BodyText, headers=headers)

        postResponse = req.json()

        new_access_token = postResponse['access_token']
        new_refresh_token = postResponse['refresh_token']

    except Exception as E:
        log.exception('Refresh token request failed')
        new_access_token = "";
        new_refresh_token = "";

    return new_access_token, new_refresh_token

def build_user_list(csv_path):
    log.info("Reading from csv path %s", csv_path)
    try:
        df = pd.read_csv(csv_path)
    except Exception as E:
        log.exception("Unable to read user CSV file")
    return df

def save_user_list(csv_path, df):
    log.info("Saving updated user CSV to path %s", csv_path)
    df.to_csv(csv_path)

def query_user_dataframe(userPath, clientID, clientSecret):
    userDF = build_user_list(userPath)
    dl = DataLoader.DataLoader(clientID, clientSecret)
    current_date = datetime.datetime.now()
    for index,row in userDF.iterrows():

        # process user information
        user_email  = row['email']
        name        = row['name']
        study_name  = row['study']
        log.info('Reading data for user %s', user_email)
        
        # process study dates for given user
        study_start_date                = row['start_date']
        study_end_date                  = row['end_date']
        study_end_datetime              = datetime.strptime(study_end_date, '%Y-%m-%d')
        study_start_datetime            = datetime.strptime(study_start_date, '%Y-%m-%d')
        
        # check if study has ended for given user
        if current_date > study_end_datetime:
            log.info('Study has ended for user %s, skipping data collection', user_email)
            continue
        
        # process access and refresh tokens, get new tokens and update dataframe
        access_token    = row['access_token']
        refresh_token   = row['refresh_token']
        new_at, new_rt = refresh_access_token(refresh_token)
        userDF.at[index, 'access_token'] = new_at
        userDF.at[index, 'refresh_token'] = new_rt

        # Begin data collection
        dl = DataLoader.DataLoader(clientID, clientSecret, study_path = AWS_PATH + study_name, pid = user_email)
        log.info("Beginning data collection for user %s", user_email)
        data_start_date = get_last_entry_date(user_email, study_name, study_start_datetime)
        num_days = 1 + get_date_delta(data_start_date, current_date)
        log.info('Loading data from dates %s to %s', data_start_date.strftime('%Y-%m-%d'), (data_start_date + datetime.timedelta(days=num_days)).strftime('%Y-%m-%d'))
        
        data, headers = query_user_data(dl, access_token, refresh_token, start_date, num_days)
        log.info("Saving data for user %s", user_email)
        save_data_files(user_email, study_name, data, headers)
        
    # save new users data frame to file
    save_user_list(userPath, userDF)


def query_list_of_users(userList, clientID, clientSecret):
    dl = DataLoader.DataLoader(clientID, clientSecret)
    current_date = datetime.datetime.now()
    for u in userList:
        user_email = u['email']
        access_token = u['auth_token']
        refresh_token = u['refresh_token']
        dl = DataLoader.DataLoader(clientID, clientSecret, study_path = AWS_PATH + 'test', pid = user_email)
        log.info('Reading data for user %s', user_email)
        start_date = STUDY_START_DATE
        num_days = 1 + get_date_delta(start_date, current_date)
        log.info('Loading data from dates %s to %s', start_date.strftime('%Y-%m-%d'), (start_date + datetime.timedelta(days=num_days)).strftime('%Y-%m-%d'))
        data, headers = query_user_data(dl, access_token, refresh_token, start_date, num_days)
        log.info('Saving data for user %s', user_email)
        save_data_files(user_email, 'test', data, headers)

def query_user_data(dataloader, access_token, refresh_token, start_date, num_days):
    log.info('Authorize user on access and refresh token')
    dataloader.authorize_client(access_token, refresh_token)
    log.info('Getting sleep, activity, heart, and user data')
    sleep_data,sleep_headers = dataloader.get_sleep_data(start_date, num_days)
    activity_data, activity_headers = dataloader.get_activity_data(start_date, num_days)
    heart_data, heart_headers = dataloader.get_heart_data(start_date, num_days)
    dataloader.get_user_data()
    
    data = {'sleep': sleep_data,
            'activity': activity_data,
            'heart': heart_data}
    headers = {'sleep': sleep_headers,
            'activity': activity_headers,
            'heart': heart_headers}

    return data, headers

def save_data_files(pid, study_name, data, headers):
    data_types = ['sleep', 'activity', 'heart']
    for dtype in data_types:
        log.info('Saving data %s as file', dtype)
        df = pd.DataFrame(data[dtype], columns=headers[dtype])
        os.makedirs(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=pid, data_name=''), exist_ok = True)
        try:
            if os.path.isfile(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=pid, data_name=dtype)):
                df.to_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=pid, data_name=dtype), mode='a', index=False, header=False)
            else:
                df.to_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=pid, data_name=dtype), index=False,columns=headers[dtype])
            log.info('Successfully saved %s data', dtype)
        except Exception as e:
            log.exception("Unable to save data %s", dtype)


def last_date_in_file(df, start_date):
    ''' finds last entry in data file, e.g. heart.csv'''
    dates = np.asarray(df['Date'])
    datetime_lst = []
    for d in dates:
        datetime_lst.append(d)
    datetime_lst.sort()
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
        log.info('Checking if user file already exists')
        df1 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='sleep'))
        date1 = last_date_in_file(df1, start_date)
        df2 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='activity'))
        date2 = last_date_in_file(df1, start_date)
        df3 = pd.read_csv(FILE_OUTPUT_STRING.format(aws_path=AWS_PATH, study_name=study_name, participant_id=user_email, data_name='heart'))
        date3 = last_date_in_file(df3, start_date)        
        log.info('User file exists, figuring out next date with no data')
    except:
        log.info('User file does not exist, starting from study start date')
        return start_date
        
    datetime_lst = [date1, date2, date3]
    datetime_lst.sort()
    log.info('User file exists, starting from next date %s + 1 day', datetime_lst[-1])
    return datetime_lst[-1]

def get_date_delta(date1, date2):
	delta = date2 - date1
	print(delta.days)
	return delta.days


def build_user_list(csv_path):
    df = pd.read_csv(csv_path)
    return df

    
#query_list_of_users(userList, clientID, clientSecret)


import fitbit
from website.gather_keys_oauth2 import *
import pandas as pd 
import datetime
from importlib import reload
import numpy as np
import website.DataLoader

CLIENT_ID = '2385BF'
CLIENT_SECRET = '34dd55f271a7630dec75ba92f7b43413'
STUDY_START_DATE = datetime.datetime.now() - datetime.timedelta(days=40)
AWS_PATH = '.'
FILE_OUTPUT_STRING = '{aws_path}/{study_name}/{participant_id}/{data_name}.csv'
DL = website.DataLoader.DataLoader(CLIENT_ID, CLIENT_SECRET)

def query_list_of_users(userList):
    print('test')

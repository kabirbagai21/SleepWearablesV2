import fitbit
import pandas as pd 
import datetime
import numpy as np
import os
from website.Sleep import *
from website.Activity import *
from website.User import *
from website.Heart import *
import json
import logging
log = logging.getLogger(__name__)

class DataLoader:
	def __init__(self, client_id, client_secret, study_path = 'test', pid='tim'):
		self.client_id = client_id
		self.client_secret = client_secret
		self.study_path = study_path
		self.pid = pid
		self.output_path = '{study_path}/{pid}/rawdata/{data_name}{date}.txt'
		try:
			log.info('making directory for study %s and user %s', study_path, pid)
			os.makedirs(study_path + '/' + pid + '/rawdata')        
		except Exception as e:
			log.exception('Directory already exists...continuing')

	def authorize_client(self, access_token, refresh_token):
		log.info('Setting up fitbit api for authorization')
		try:
			self.auth2_client = fitbit.Fitbit(self.client_id, self.client_secret, oauth2=True, access_token=access_token, refresh_token=refresh_token)
		except Exception as e:
			log.exception('Authorization failed, please check access and refresh tokens')

	def get_sleep_data(self, start_date, num_days): 
		end_date = start_date + datetime.timedelta(days=num_days)
		sleepLoader = Sleep(self.auth2_client)
		sleep_data_stored = []
		sleep_headers = ['Date', 'FitbitDataType', 'MinutesAsleep', 'MinutesAwake', 'Awakenings', 'Deep', 'Light', 'REM', 'Wake', 'DeepCount', 'LightCount', 'REMCount', 'WakeCount', 'asleepTimeClassic', 'awakeTimeClassic', 'restlessTimeClassic', 'asleepCountClassic', 'awakeCountClassic', 'restlessCountClassic', 'StartTime', 'EndTime', 'MainDuration', 'SleepEfficiency', 'isMainSleep', 'minutesAfterWakeup', 'minutesToFallAsleep', 'timeInBed', 'userid']
		log.info('Getting sleep data between dates %s and %s', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
		sleep_data = sleepLoader.get_sleep_data(start_date, end_date)
		try:
			num_sleep_periods = len(sleep_data['sleep'])
		except:
			log.exception("No sleep data returned")
			return [], sleep_headers
        
		for i in range(len(sleep_data['sleep'])):
			date = start_date + datetime.timedelta(days=i)
			info = sleep_data['sleep'][i]
			try:
				date = sleepLoader.get_sleep_date(info)
				log.info('Saving JSON file to user directory')
				with open(self.output_path.format(study_path=self.study_path,pid=self.pid,data_name='sleep', date=date), 'w') as convert_file:
					convert_file.write(json.dumps(info))
			except Exception as e:
				log.exception('Unable to save sleep JSON for date')

			main_sleep = sleep_data['sleep'][i]
			if main_sleep['type'] == 'classic':
				log.info('Processing sleep data for classic type')
				entry = self.process_sleep_data_classic(sleepLoader,main_sleep)
			else:
				log.info('Processing sleep data for stages type')
				entry = self.process_sleep_data_stages(sleepLoader,main_sleep)
			sleep_data_stored.append(entry)
		log.info('Successfully processed sleep data for data ranges %s and %s', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
		return sleep_data_stored, sleep_headers

	def process_sleep_data_stages(self, sleepLoader, json):
		log.info('Processing sleep information')
		date = sleepLoader.get_sleep_date(json)
		minutesawake = sleepLoader.get_minutes_awake(json)
		minutesasleep = sleepLoader.get_minutes_asleep(json)
		starttime, endtime = sleepLoader.get_sleep_times(json)
		awakenings = sleepLoader.get_num_awakenings(json)
		wake, light, deep, rem = sleepLoader.get_sleep_stage_times(json)	
		wakec, lightc, deepc, remc =sleepLoader.get_sleep_stage_counts(json)
		asleep = 0
		asleepc = 0
		awake = 0
		awakec = 0
		restless = 0
		restlessc = 0
		main_sleep = sleepLoader.get_is_nap(json)
		se = sleepLoader.get_sleep_efficiency(json)
		dur = sleepLoader.get_main_sleep_duration(json)
		minutesAfterWakeup = sleepLoader.get_minutes_after_wakeup(json)
		minutesToFallAsleep = sleepLoader.get_minutes_to_fall_asleep(json)
		timeInBed = sleepLoader.get_time_in_bed(json)
		data_list = [date, json['type'], minutesasleep, minutesawake, awakenings, deep, light, rem, wake, deepc, lightc, remc, wakec, asleep, awake, restless, asleepc, awakec, restlessc, starttime, endtime, dur, se, main_sleep, minutesAfterWakeup, minutesToFallAsleep, timeInBed, self.pid]
		log.info('Finish processing sleep data')
		return data_list
               
	def process_sleep_data_classic(self, sleepLoader, json):
		log.info('Processing sleep information')
		date = sleepLoader.get_sleep_date(json)
		minutesawake = sleepLoader.get_minutes_awake(json)
		minutesasleep = sleepLoader.get_minutes_asleep(json)
		starttime, endtime = sleepLoader.get_sleep_times(json)
		awakenings = sleepLoader.get_num_awakenings(json)
		wake = 0
		wakec = 0
		light = 0
		lightc = 0 
		deep = 0
		deepc = 0 
		rem = 0
		remc = 0
		asleep, awake, restless = sleepLoader.get_classic_sleep_times(json)
		asleepc, awakec, restlessc = sleepLoader.get_classic_sleep_counts(json)
		main_sleep = sleepLoader.get_is_nap(json)
		se = sleepLoader.get_sleep_efficiency(json)
		dur = sleepLoader.get_main_sleep_duration(json)
		minutesAfterWakeup = sleepLoader.get_minutes_after_wakeup(json)
		minutesToFallAsleep = sleepLoader.get_minutes_to_fall_asleep(json)
		timeInBed = sleepLoader.get_time_in_bed(json)
		data_list = [date, json['type'], minutesasleep, minutesawake, awakenings, deep, light, rem, wake, deepc, lightc, remc, wakec, asleep, awake, restless, asleepc, awakec, restlessc, starttime, endtime, dur, se, main_sleep, minutesAfterWakeup, minutesToFallAsleep, timeInBed, self.pid]
		log.info('Finish processing sleep data')
		return data_list

    
	def get_activity_data(self, start_date, num_days):
		end_date = start_date + datetime.timedelta(days=num_days)
		activityLoader = Activity(self.auth2_client)
		activity_data = []
		activity_headers = ['NumActivities', 'activescore', 'activeCalories', 'caloriesBMR', 'caloriesOut', 'marginalCalories', 'restingHeartRate', 'Steps', 'lightlyActiveMinutes', 'veryActiveMinutes', 'sedentaryMinutes', 'fairlyActiveMinutes', 'Date', 'userid']
        
		activityLoader = Activity(self.auth2_client)

		for i in range(num_days+1):
			date_string = str((start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d"))
			jsonActivity = activityLoader.get_activity_data(date_string)
			date = str((start_date + datetime.timedelta(days=i)).strftime('%Y%m%d'))
			with open(self.output_path.format(study_path=self.study_path,pid=self.pid,data_name='activity', date=date), 'w') as convert_file:
				convert_file.write(json.dumps(jsonActivity))
			entry = self.process_activity_data(activityLoader, jsonActivity)
			entry.append(date_string)
			activity_data.append(entry)
		return activity_data, activity_headers
    
	def process_activity_data(self, activityLoader, json):
		laMinutes, vaMinutes, sMinutes, faMinutes = activityLoader.get_minute_breakdowns(json)
		activecalories, caloriesBMR, caloriesOut, marginalCalories = activityLoader.get_calories_data(json)
		rhr = activityLoader.get_rhr(json)
		score = activityLoader.get_activity_score(json)
		total_steps = activityLoader.get_steps(json)
		numact = activityLoader.get_num_activities(json)
		return [numact, score, activecalories, caloriesBMR, caloriesOut, marginalCalories, rhr, total_steps, laMinutes, vaMinutes, sMinutes, faMinutes, self.pid]
        
        
	def get_user_data(self):
		userLoader = User(self.auth2_client)
		userJson = userLoader.get_user_data()
		with open(self.output_path.format(study_path=self.study_path,pid=self.pid,data_name='userprofile', date=''), 'w') as convert_file:
			convert_file.write(json.dumps(userJson))
 
    
	def get_heart_data(self, start_date, num_days):
		end_date = start_date + datetime.timedelta(days=num_days)
		heartLoader = Heart(self.auth2_client)
        
		heart_headers = ['Date', 'OutofRange', 'FatBurn', 'Cardio', 'Peak', 'userid']
		heart_data = []
		heart_json = heartLoader.get_heart_data(start_date, end_date)
		try:
			num_heart_entries = len(heart_json['activities-heart'])
		except Exception as e:
			log.exception("No heart rate data")
			return [], heart_headers
		for i in range(len(heart_json['activities-heart'])):
			date = start_date + datetime.timedelta(days=i)
			with open(self.output_path.format(study_path=self.study_path,pid=self.pid,data_name='heart', date=date.strftime('%Y%m%d')), 'w') as convert_file:
				convert_file.write(json.dumps(heart_json['activities-heart'][i]))
			entry = self.process_heart_data(heartLoader, heart_json['activities-heart'][i])
			heart_data.append(entry)
		return heart_data, heart_headers
	
	def process_heart_data(self, heartLoader, json):
		date = heartLoader.get_date(json)
		oor_time, fb_time, c_time, p_time = heartLoader.time_HR_zones(json)
		return [date, oor_time, fb_time, c_time, p_time, self.pid]
      

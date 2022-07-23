import pandas as pd
import logging
log = logging.getLogger(__name__)

class Activity:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        
    def get_activity_data(self, date):
        try:
            log.info("Retrieving activity data for date %s", date)
            return self.auth_client.activities(date=date)
        except Exception as e:
            log.exception('Unable to retrieve activity data for date %s', date)
            return []
        
    @staticmethod
    def get_minute_breakdowns(json):
        try:
            log.info('Getting activity minutes breakdown from JSON file')
            lamin = int(json['summary']['lightlyActiveMinutes'])
            vamin = int(json['summary']['veryActiveMinutes'])
            smin = int(json['summary']['sedentaryMinutes'])
            famin = int(json['summary']['fairlyActiveMinutes'])
        except Exception as e:
            log.exception('Unable to retrieve activity minutes breakdown')
            lamin = 0
            vamin = 0
            smin = 0
            famin = 0
        return lamin, vamin, smin, famin
    
    @staticmethod
    def get_calories_data(json):
        try:
            log.info('Get active calories')
            activecalories = int(json['summary']['activityCalories'])
        except Exception as e:
            log.exception('Unable to retrieve active calories')
            activecalories = 0
        try:
            log.info('Get BMR calories')
            caloriesBMR = int(json['summary']['caloriesBMR'])
        except Exception as e:
            log.exception('Unable to retrieve BMR calories')
            caloriesBMR = 0
        try:
            log.info('Get out calories')
            caloriesOut = int(json['summary']['caloriesOut'])
        except Exception as e:
            log.exception('Unable to retrieve out calories')
            caloriesOut = 0
        try:
            log.info('Get marginal calories')
            marginalCalories = int(json['summary']['marginalCalories'])
        except Exception as e:
            log.exception('Unable to retrieve marginal calories')
            marginalCalories = 0

        return activecalories, caloriesBMR, caloriesOut, marginalCalories

    @staticmethod
    def get_activity_score(json):
        try:
            log.info('Getting activity score')
            score = int(json['summary']['activeScore'])
        except Exception as e:
            log.exception('No activity score')
            score = 0
        return score
    
    @staticmethod
    def get_rhr(json):
        try:
            log.info('Get RHR')
            rhr = int(json['summary']['restingHeartRate'])
        except Exception as e:
            log.exception('Unable to retrieve RHR') 
            rhr = 0
        return rhr
    
    @staticmethod
    def get_steps(json):
        try:
            log.info('Getting daily steps')
            steps = int(json['summary']['steps'])
        except Exception as e:
            log.exception('Unable to retrieve daily steps')
            steps = 0
        return steps
    
    @staticmethod
    def get_num_activities(json):
        try:
            log.info('Getting number of activities')
            num_act = len(json['activities'])
        except Exception as e:
            log.exception('Unable to retrieve number of activities')
            num_act = 0
        return num_act

import pandas as pd
import datetime
import logging
log = logging.getLogger(__name__)

class Sleep:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        
    def get_sleep_data(self, sdate, edate=None):
        try:
            log.info('Accessing sleep data for given range from FitBit API')
            data = self.auth_client.get_sleep_range(sDate=sdate, eDate=edate)
        except Exception as E:
            log.exception('Unable to call FitBit API')
            data = []
        return data
        
    @staticmethod
    def get_minutes_awake(json):
        try:
            log.info('Getting minutes awake from JSON file')
            return int(json['minutesAwake'])
        except Exception as e:
            log.exception('Unable to retrieve minutes awake, outputting 0')
            return 0
        
    @staticmethod  
    def get_is_nap(json):
        try:
            log.info('Getting nap/main sleep from JSON file')
            return json['isMainSleep']
        except Exception as e:
            log.exception('Unable to access main sleep data')
            return True
    
    @staticmethod
    def get_minutes_after_wakeup(json):
        try:
            log.info('Getting minutes after wakeup from JSON file')
            return int(json['minutesAfterWakeup'])
        except Exception as e:
            log.exception('Unable to get minutes after wakeup')
            return 0
    
    @staticmethod
    def get_time_in_bed(json):
        try:
            log.info('Getting time in bed from JSON file')            
            return int(json['timeInBed'])
        except Exception as e:
            log.exception('Unable to get time in bed')
            return 0

    @staticmethod
    def get_minutes_to_fall_asleep(json):
        try:
            log.info('Getting minutes to fall asleep from JSON file')
            return int(json['minutesToFallAsleep'])
        except Exception as e:
            log.exception('Unable to get minutes to fall asleep')
            return 0
    
    @staticmethod
    def get_minutes_asleep(json):
        try:
            log.info('Getting minutes asleep')
            return int(json['minutesAsleep'])
        except Exception as e:
            log.exception('Unable to get minutes asleep')
            return 0
        
    @staticmethod
    def get_sleep_times(main_sleep):
        try:
            log.info('Getting sleep start and end time from JSON file')
            start_time = main_sleep['startTime']
            end_time = main_sleep['endTime']
        except Exception as e:
            log.exception('Unable to retrieve sleep start and end times')
            start_time = 0
            end_time = 0
        return start_time, end_time

    @staticmethod
    def get_num_awakenings(main_sleep):
        try:
            log.info('Getting number of awakenings during sleep from JSON file')
            return int(main_sleep['levels']['summary']['wake']['count'])
        except Exception as e:
            try:
                return int(main_sleep['levels']['summary']['awake']['count'])
            except Exception as e:
                log.exception('Unable to retrieve number of awakenings')
                return 0
    
    @staticmethod
    def get_sleep_date(main_sleep):
        try:
            log.info('Getting data of sleep from JSON file')
            return main_sleep['dateOfSleep']
        except Exception as e:
            log.exception('Unable to retrieve date of sleep')
            return "1900-00-00"
        
    @staticmethod
    def get_sleep_stage_times(json):
        try:
            log.info('Getting sleep staging data (minutes) from JSON file')
            deep = int(json['levels']['summary']['deep']['minutes'])
            light = int(json['levels']['summary']['light']['minutes'])
            rem = int(json['levels']['summary']['rem']['minutes'])
            wake = int(json['levels']['summary']['wake']['minutes'])
        except Exception as e:
            log.exception('Unable to retrieve sleep staging data (minutes)')
            deep = 0
            light = 0
            rem = 0
            wake = 0
        return wake, light, deep, rem
        
    @staticmethod
    def get_sleep_stage_counts(json):
        try:
            log.info('Getting sleep staging data (counts) from JSON file')
            deep = int(json['levels']['summary']['deep']['count'])
            light = int(json['levels']['summary']['light']['count'])
            rem = int(json['levels']['summary']['rem']['count'])
            wake = int(json['levels']['summary']['wake']['count'])
        except Exception as e:
            log.exception('Unable to retrieve sleep staging data (counts)')
            deep = 0
            light = 0
            rem = 0
            wake = 0
        return wake, light, deep, rem
        
    @staticmethod
    def get_classic_sleep_times(json):
        try:
            log.info('Getting sleep classic data (minutes) from JSON file')
            asleep = int(json['levels']['summary']['asleep']['minutes'])
            awake = int(json['levels']['summary']['awake']['minutes'])
            restless = int(json['levels']['summary']['restless']['minutes'])
        except Exception as e:
            log.exception('Unable to retrieve sleep classic data (minutes)')
            asleep = 0
            awake = 0
            restless = 0
        return asleep, awake, restless
        
    @staticmethod
    def get_classic_sleep_counts(json):
        try:
            log.info('Getting sleep classic data (minutes) from JSON file')
            asleep = int(json['levels']['summary']['asleep']['count'])
            awake = int(json['levels']['summary']['awake']['count'])
            restless = int(json['levels']['summary']['restless']['count'])
        except Exception as e:
            log.exception('Unable to retrieve sleep classic data (counts)')
            asleep = 0
            awake = 0
            restless = 0
        return asleep, awake, restless
    
    @staticmethod
    def get_main_sleep_duration(main_sleep):
        try:
            log.info('Get sleep duration from JSON')
            dur = int(main_sleep['duration'])
        except Exception as e:
            log.exception('Unable to get sleep duration') 
            dur = 0
        return dur
    
    @staticmethod
    def get_sleep_efficiency(main_sleep):
        try:
            log.info('Retrieving sleep efficiency from JSON')
            se = float(main_sleep['efficiency'])
        except Exception as e:
            log.exception('Unable to retrieve sleep efficiency')
            se = 0.0
        return se

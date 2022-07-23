import pandas as pd
import logging
log = logging.getLogger(__name__)

class Heart:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        
    def get_heart_data(self, date, end_date, period='1d'):
        try:
            log.info('Getting heart rate data for range %s to %s', date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            return self.auth_client.time_series('activities/heart', base_date=date, end_date = end_date)
        except Exception as E:
            log.exception('Unable to retrieve heart rate data')
            return []
    
    @staticmethod
    def time_HR_zones(HRjson):
        hr_zones = ['Out of Range', 'Fat Burn', 'Cardio', 'Peak']
        hr_times = {}
        try:
            log.info('Getting times in each heart rate zone')
            rel_json = HRjson['value']['heartRateZones']
            for component in rel_json:
                name = component['name']
                hr_times[name] = int(component['minutes'])
            
            oor_time = hr_times[hr_zones[0]]
            fb_time = hr_times[hr_zones[1]]
            c_time = hr_times[hr_zones[2]]
            p_time = hr_times[hr_zones[3]]
        except Exception as e:
            log.exception('Unable to retrieve time zones in each heart rate zone')
            oor_time = 0
            fb_time = 0
            c_time = 0
            p_time = 0
        return oor_time, fb_time, c_time, p_time
    
    @staticmethod
    def get_date(HRjson):
        try:
            log.info('Getting date of json file')
            return HRjson['dateTime']
        except Exception as e:
            log.exception('Unable to retrieve date')
            return '1900-00-00'
    

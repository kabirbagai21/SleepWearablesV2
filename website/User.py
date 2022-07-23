import logging
log = logging.getLogger(__name__)

class User:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        
    def get_user_data(self):
        try:
            log.info('Querying fitbit api for user profile')
            data = self.auth_client.user_profile_get()
            return data
        except Exception as e:
            log.exeption('Unable to retrive user profile')
    
    @staticmethod
    def get_user_name(json):
        return json['user']['fullName']
    
    @staticmethod
    def get_user_birthday(json):
        return json['user']['dateOfBirth']
    
    @staticmethod
    def get_user_gender(json):
        return json['user']['gender']
    
    @staticmethod
    def get_user_sleep_tracking(json):
        return json['user']['sleepTracking']
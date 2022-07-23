
from flask import Blueprint, redirect, render_template, request, flash
from query_data import *
from .models import User
from . import db
from flask_login import current_user, login_required, login_user
import requests
import logging
import csv
from csv import writer 

log = logging.getLogger(__name__)
views = Blueprint('views', __name__)

clientID = "2385BF"
clientSecret = "34dd55f271a7630dec75ba92f7b43413"
encodedID_Secret = 'MjM4NUJGOjM0ZGQ1NWYyNzFhNzYzMGRlYzc1YmE5MmY3YjQzNDEz'
#clientID = "238BMP"
#clientSecret = "9fc1aafb884bce948bd812995b2fd985"
#encodedID_Secret = 'MjM4Qk1QOjlmYzFhYWZiODg0YmNlOTQ4YmQ4MTI5OTViMmZkOTg1'
TokenURL = "https://api.fitbit.com/oauth2/token"


def getAccessToken(authCode):
    BodyText = {'code' : authCode,
                'redirect_uri' : 'http://127.0.0.1:5000/final',
                'client_id' : clientID,
                'grant_type' : 'authorization_code'}

    headers = {'Authorization': 'Basic ' + encodedID_Secret, 
        'Content-Type': 'application/x-www-form-urlencoded'}  
    
    try:
        log.info('Sending post request for access token')
        req = requests.post(TokenURL, params=BodyText, headers= headers)

        postResponse = req.json() 

        access_token = postResponse['access_token']
        refresh_token = postResponse['refresh_token']
        scopes = postResponse['scope']
    
    except Exception as E:
        log.exception('Access token request failed')
        access_token = ""; 
        refresh_token = ""; 
        scopes = ""

    return access_token, refresh_token, scopes


def initCSV():
    
    filename = '/Users/kabirbagai/Desktop/SleepWearablesV2/website/users.csv'
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        fields = ['Name', 'Email', 'Study', 'Start Date', 'End Date' 'Auth Token', 'Refresh Token', 'Scopes']
        writer.writerow(fields) 
        f.close()
        

def writeNewLine(curr_user):
    filename = '/Users/kabirbagai/Desktop/SleepWearablesV2/website/users.csv'
    file = open(filename, "r")
    file_content = file.read()
    file.close()
    if file_content == "":
       initCSV()
        

    with open(filename, 'a+', newline='') as write_obj:
    
        csvwriter = writer(write_obj) 
        
        row = [curr_user.firstname, curr_user.email, curr_user.study_name, curr_user.study_start_date,
        curr_user.study_end_date, curr_user.auth_token, curr_user.refresh_token, curr_user.scopes]
        
        csvwriter.writerow(row)
        write_obj.close()


def clearFile():
    filename = '/home/ec2-user/SleepWearablesV2/website/users.csv'
    f = open(filename, "w+")
    initCSV()
    f.close()



@views.route('/<firstname>/<email>/<study>/<study_start_date>/<study_end_date>', methods=['GET', 'POST'])
def home(firstname, email, study, study_start_date, study_end_date):
    user = User.query.filter_by(email=email).first()
    
    if user:
        flash('Email already exists.', category='error')
    
    else:
        new_user = User(firstname=firstname, email=email, study_name = study,  
        study_start_date=study_start_date, study_end_date = study_end_date,
        auth_token="", refresh_token="", scopes = "")

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)

        try:
            log.info('Redirecting to fitbit auth page')
            return redirect('https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=2385BF&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Ffinal&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight%20oxygen_saturation%20respiratory_rate&expires_in=604800')
        except Exception as E:
            log.exception('Redirect failed')
     
        

    return render_template("home.html", user = current_user)

@login_required
@views.route('/final', methods=['GET', 'POST'])
def final():
    if request.method == 'GET':
        code = request.args.get('code')
    tokens = getAccessToken(code)
    
    try: 
        log.info('Adding new tokens to user object in database')
        current_user.auth_token = tokens[0]
        current_user.refresh_token = tokens[1]
        current_user.scopes = tokens[2]
        db.session.commit()
    except Exception as E:
        log.exception('Failed to add tokens or scopes')    
   
    try:
       writeNewLine(current_user)
       log.info("added user info to csv")
    except: 
        log.warning("failed to write to csv file")

    return render_template("final.html", user = current_user)

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

@views.route('/transfer')
def transfer():
    ls_dict = []
    users = User.query.order_by(User.id);
  

    for u in users:
       
        try:
            at, rt = refreshAccessToken(u.refresh_token)
            u.auth_token = at
            u.refresh_token = rt
            db.session.commit()
        except:
            log.warning("Failed to update current user's tokens")
            continue
        
        dict = {'email': u.email, 'auth_token': at, 'refresh_token': rt, 'id': u.id}
        ls_dict.append(dict);
   

    print(ls_dict)
    #query_list_of_users(ls_dict, clientID, clientSecret); 
    return render_template("transfer.html"); 







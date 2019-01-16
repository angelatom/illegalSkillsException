'''
IllegalSkillsException
Aaron Li, Angela Tom, Kevin Lin, Max Millar
Softdev1 pd6
P#02 -- Final Project
2019-01-09
'''

import os
import flask
import requests
import json
import datetime

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from urllib import request, parse
import sqlite3

from util import dbtools as db
from util import quotes as q

app = flask.Flask(__name__)
app.secret_key = os.urandom(32)

# client secret key
with open("keys/client_secret.json") as key:
	api_keys = json.load(key)

client_secret = "keys/client_secret.json"
# necessary info (given by google api for auth)
client_id = api_keys["web"]["client_id"]
#client_secret = api_keys["web"]["client_secret"]
redirect_uri = "http://localhost:5000/oauth2callback"
auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
refresh_url = token_url
scope = [
    'https://www.googleapis.com/auth/calendar',
	'https://www.googleapis.com/auth/calendar.events'
]

API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

# save token in session
def token_saver(token):
	flask.session["credentials"] = token

# for student uploads
UPLOAD_FOLDER = './data/studentUploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# login page
@app.route('/')
def index():
	#print(quotes.get_random_quote())
	return flask.render_template("login.html")

# logged in page
@app.route('/login')
def login():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

  # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
    calendar = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    entry = calendar.calendars().get(calendarId='primary').execute()
    #print(entry)
	# DONT TOUCH
    userID = db.getUserID(entry["id"])
    flask.session["email"] = entry["id"] # add email
    if userID == None: #User is not registered
        flask.session['userid'] = db.registerUser(entry["id"])
        return flask.render_template("register.html")
    else:
        flask.session['userid'] = userID
        userInfo = db.getUserInfo(flask.session['userid'])
        name = userInfo[0]
        classNamesT = [i[1] for i in userInfo[2]] #List of names for classes being taught
        classIDsT = [i[0] for i in userInfo[2]] #List of class IDs for classes being taught
        classNamesE = [i[1] for i in userInfo[1]] #List of names for enrolled classes
        classIDsE = [i[0] for i in userInfo[1]] #List of class IDs for enrolled classes
    #name = calendar.get("")
    #return flask.redirect("index.html")
    return flask.render_template("index.html", name = name, classnames = classNamesT,
		classids = classIDsT, enrolleds = userInfo[1], teachings = userInfo[2])

# authorize (send user to auth url with necessary params)
@app.route("/authorize")
def auth():
   # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secret, scopes=scope)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
    access_type='offline', include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)

def credentials_to_dict(credentials):
    return {'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes}


# callback url (exchange auth code for access token)
@app.route("/oauth2callback", methods=["GET"])
def oauth2callback():
	state = flask.session['state']

	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		client_secret, scopes=scope, state=state)
	flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

	# Use the authorization server's response to fetch the OAuth 2.0 tokens.
	authorization_response = flask.request.url
	flow.fetch_token(authorization_response=authorization_response)

	credentials = flow.credentials
	flask.session['credentials'] = credentials_to_dict(credentials)

	return flask.redirect("/login")


# logout
@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials'] # remove token
        del flask.session['userid'] # remove userid
    flask.flash("Logout successful!")
    return (flask.redirect("/"))

# register
@app.route('/regname', methods=["POST"])
def regname():
    name = flask.request.form['name']
    db.updateName(flask.session['userid'], name)
    return flask.redirect('/login')

# make a class
@app.route('/makeclass')
def makeClass():
    return flask.render_template("makeclass.html")

@app.route('/processmakeclass', methods=['POST'])
def processMakeclass():
	classname = flask.request.form['classname']
	weightnames = flask.request.form.getlist('weightnames')
	weightnums = flask.request.form.getlist('weightnums')
	desc = flask.request.form['desc']
	weightList = []
	for i in range(len(weightnames)):
		toAppend = [weightnames[i],weightnums[i]]
		weightList.append(toAppend)
	db.createClass(classname, flask.session["userid"], weightList, desc)
	classname = classname + ""
	cal = {
    'summary': classname,
    'timeZone': 'America/New_York'
	}
	credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
	service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
	created_calendar = service.calendars().insert(body=cal).execute()
	WE_NEED_TO_SAVE_THIS = created_calendar['id']
	return flask.redirect("/login")

@app.route('/class/<classid>')
def classpage(classid):
    if 'userid' not in flask.session:
    	return flask.redirect('/')
    classInfo = db.getClassInfo(classid)
    classRoster = db.getRoster(classid)
    isTeacher = (db.getTeacher(classid) == flask.session["userid"])
    posts = db.getPosts(classid)
    return flask.render_template("class.html", className = classInfo[0],
		teacherName = db.getUserName(classInfo[1]), inviteCode = classInfo[2],
		weights = classInfo[3], classRoster = classRoster, getName = db.getUserName,
		isTeacher = isTeacher, classID = classid, posts = posts[::-1],
		getPostFiles = db.getPostFiles, desc = classInfo[4])

@app.route('/invite/<inviteCode>')
def acceptInvite(inviteCode):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	result = db.acceptInvite(flask.session['userid'], inviteCode)
	flask.flash(result)
	return flask.redirect('/login')

@app.route('/invite', methods=["POST"])
def invite():
	if 'userid' not in flask.session:
		return flask.redirect('/')
	result = db.acceptInvite(flask.session['userid'], flask.request.form['inviteCode'])
	flask.flash(result)
	return flask.redirect(flask.request.referrer)


@app.route('/gradebook/<classid>/<assignment>')
def gradebook(classid, assignment):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	classInfo = db.getClassInfo(classid)
	if not db.isTeacher(flask.session['userid'], classid):
		return "User is not the teacher of this class."
	classRoster = db.getRoster(classid)
	maxGrade,gradeDict = db.getAssignmentGrades(classid, assignment)
	return flask.render_template("gradebook.html", className = classInfo[0],
		assignment = assignment, roster = classRoster, gradeDict = gradeDict,
		getName = db.getUserName, classID = classid, maxGrade = maxGrade,
		weights = classInfo[3])

#
@app.route('/submitGrades', methods = ["POST"])
def submitGrades():
	inputs = [None, None, None, None, None]
	for i in flask.request.form:
		print(i)
	try:
		inputs[0] = flask.request.form['classID']
		studentIDs = flask.request.form.getlist('studentID')
		studentGrades = flask.request.form.getlist('grade')
		inputs[4] = flask.request.form['weight']
		gradesList = []
		for i in range(len(studentIDs)):
			toAppend = [None, None] #[userID, grade]
			try:
				toAppend[1] = int(studentGrades[i])
			except:
				continue
			toAppend[0] = studentIDs[0]
			gradesList.append(toAppend)
		inputs[1] = gradesList
		inputs[2] = flask.request.form['assignment']
		inputs[3] = int(flask.request.form['maxGrade'])
	except:
		return "Invalid input(s)."
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if not db.isTeacher(flask.session['userid'],inputs[0]):
		return "User is not the teacher of this class."
	db.changeGrades(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4])
	return "Grade update successful."


# fix the return to an html page
@app.route('/submitFile', methods = ["POST"])
def submitFile():
	if 'userid' not in flask.session:
		return flask.redirect('/')
	classID = db.getClassID(flask.request.form['postID'])
	if db.isEnrolled(flask.session['userid'], classID):
		if 'file' not in flask.request.files:
			return "No file submitted."
		file = flask.request.files['file']
		if file.filename == '':
			return "No file submitted."
		if file:
			filename = db.addFile(flask.request.form['postID'], flask.session['userid'])
			filename += '.txt' #Makes all files have a .txt extension
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return "File submission successful."
	else:
		return "User is not enrolled in this class."

@app.route('/makepost/<classID>')
def makePost(classID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if not db.isTeacher(flask.session['userid'], classID): # block students accessing teacher pages
		return "User is not the teacher of this class."
	date = str(datetime.date.today())
	return flask.render_template("makepost.html", date=date, classID=classID)

@app.route('/processmakepost/<classID>', methods=['POST'])
def processMakePost(classID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if not db.isTeacher(flask.session['userid'], classID):
		return "User is not the teacher of this class."
	postbody = flask.request.form['postbody']
	duedate = flask.request.form['duedate']
	duetime = flask.request.form['duetime']
	submittable = flask.request.form.get('submittable')
	if submittable == None:
		submittable = 0
	else:
		submittable = 1
	due = duedate + " " + duetime
	db.makePost(classID, due, postbody, submittable)
	return flask.redirect('/class/' + classID)

# This file must be a txt file
@app.route('/viewFile/<filename>', methods=['GET'])
def viewFile(filename):
	fileExists = db.fileExists(filename)
	if fileExists:
		file = open("./data/studentUploads/" + filename + ".txt","r")
		output = file.read()
		file.close()
		return flask.render_template('viewfile.html', fileContent = output)
	else:
		return "File does not exist."

@app.route('/deleteclass/<classID>')
def deleteClass(classID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if not db.isTeacher(flask.session['userid'], classID):
		return "User is not the teacher of this class."
	db.deleteClass(classID)
	return flask.redirect('/login')

@app.route('/deletepost/<postID>')
def deletePost(postID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	classID = db.getClassID(postID)
	if not db.isTeacher(flask.session['userid'], classID):
		return "User is not the teacher of this class."
	db.deletePost(postID)
	return flask.redirect('/class/' + str(classID))

@app.route('/usergrades/<classID>/<userID>')
def userGrades(classID, userID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if flask.session['userid'] != userID:
		if not db.isTeacher(flask.session['userid'], classID):
			return flask.redirect('/class/' + str(classID))
	avg,weightavgs = db.calculateAverage(userID, classID)
	name = db.getUserName(userID)
	grades = db.getUserGrades(classID, userID)
	return flask.render_template('usergrades.html', avg = avg, weightavgs = weightavgs, name = name, grades = grades)

@app.route('/editclass/<classID>', methods=["POST"])
def editClass(classID):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	if not db.isTeacher(flask.session['userid'], classID):
		return "User is not the teacher of this class."
	classname = flask.request.form['classname']
	weightnames = flask.request.form.getlist('weightnames')
	weightnums = flask.request.form.getlist('weightnums')
	desc = flask.request.form['desc']
	weightList = []
	for i in range(len(weightnames)):
		toAppend = [weightnames[i],weightnums[i]]
		weightList.append(toAppend)
	db.editClass(classID, classname, desc, weightList)
	return flask.redirect('/class/' + str(classID))

@app.route('/quotes')
def quote():
	return q.get_random_quote()
'''
def google_calendar():
	if 'userid' not in flask.session:
		return flask.redirect('/')
	start_time = db.
	event = {
		'start': {
			'dateTime': '2015-05-28T09:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
		},
		'end': {
			'dateTime': '2015-05-28T17:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
		},
	}
	try:
		calendar = OAuth2Session(client_id, token=flask.session["credentials"])
		entry = calendar.post('https://www.googleapis.com/calendar/v3/calendars/primary/events', event)
	# for refresh token
	except TokenExpiredError as e:
		token = flask.session["credentials"]
		extra = {
			'client_id': client_id,
			'client_secret': client_secret,
		}
		calendar = OAuth2Session(client_id, token=token)
		flask.session['credentials'] = calendar.refresh_token(refresh_url, **extra)
	calendar = OAuth2Session(client_id, token=flask.session["credentials"])
	entry = calendar.post('https://www.googleapis.com/calendar/v3/calendars/primary/events', event)
	return entry
'''
if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # can use http urls
    app.run(debug = True)

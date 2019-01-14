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

# for oauth
from requests_oauthlib import OAuth2Session
# for using refresh tokens when there is a token expired error
from oauthlib.oauth2 import TokenExpiredError

from urllib import request, parse
import sqlite3

from util import dbtools as db

app = flask.Flask(__name__)
app.secret_key = os.urandom(32)

# client secret key
with open("keys/client_secret.json") as key:
	api_keys = json.load(key)

# necessary info (given by google api for auth)
client_id = api_keys["web"]["client_id"]
client_secret = api_keys["web"]["client_secret"]
redirect_uri = "http://localhost:5000/oauth2callback"
auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
refresh_url = token_url
scope = [
    'https://www.googleapis.com/auth/calendar'
]

# for refresh token
extra = {
    'client_id': client_id,
    'client_secret': client_secret,
	}

# save token in session
def token_saver(token):
	flask.session["credentials"] = token

# for student uploads
UPLOAD_FOLDER = './data/studentUploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# login page
@app.route('/')
def index():
	'''
	calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    #entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    #print(entry)
	token=flask.session["credentials"]
	print(token)
	token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
    #flask.session["credentials"] = token # store new token
	print(token)
	'''
	return flask.render_template("login.html")
	'''
	# TESTING STUFF
	calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    #entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    #print(entry)
	token = flask.session["credentials"]
	print(token)
	token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
    #flask.session["credentials"] = token # store new token
	print(token)
    #return ('<a href="/login"> Login with Google</a>')
	'''

# logged in page
@app.route('/login')
def login():
    if "credentials" not in flask.session:
        return flask.redirect("authorize") # redirect if acess token is not there
    '''
    calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    #entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    #print(entry)
    token=flask.session["credentials"]
    print(token)
    token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
    #flask.session["credentials"] = token # store new token
    print(token)

    calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    #entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    #print(entry)
    token = flask.session["credentials"]
    print(token)
    token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
    #flask.session["credentials"] = token # store new token
    print(token)

    token = flask.session["credentials"]
    calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    print(token)
    token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
    print(token)
	'''
	# try, except block for refresh tokens in case of expired token error
    calendar = OAuth2Session(client_id, token=flask.session["credentials"], auto_refresh_url=refresh_url,
        auto_refresh_kwargs=extra, token_updater=token_saver)
        #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    #print(entry)
    '''
    except TokenExpiredError as e:
		# refresh token
		calendar = OAuth2Session(client_id, token=flask.session["credentials"], auto_refresh_url=refresh_url,
     auto_refresh_kwargs=extra, token_updater=token_saver)
        #token = calendar.refresh_token(refresh_url, {"client id": client_id, "client_secret": client_secret})
        flask.session["credentials"] = token # store new token
    calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    entry = calendar.get("https://www.googleapis.com/calendar/v3/users/me/calendarList/primary").json()
    '''
    userID = db.getUserID(entry["id"])
    email = entry["id"]
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
		classids = classIDsT, email=email, enrolleds = userInfo[1], teachings = userInfo[2])

# authorize (send user to auth url with necessary params)
@app.route("/authorize")
def auth():
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(auth_base_url,
    access_type="offline", include_granted_scopes="true") #offline for refresh token, granted scopes to show the user what we have access to
    flask.session["state"] = state # state validates response to ensure that request/response originated in same browser
    return flask.redirect(authorization_url) #OAuth provider authorizes user and sends back user to callback URL with auth code and state

# callback url (exchange auth code for access token)
@app.route("/oauth2callback", methods=["GET"])
def callback():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=flask.session['state'])
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=flask.request.url)
    # fetch token
    flask.session["credentials"] = token # store token
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
    return flask.redirect("/login")

@app.route('/class/<classid>')
def classpage(classid):
    classInfo = db.getClassInfo(classid)
    classRoster = db.getRoster(classid)
    isTeacher = (db.getTeacher(classid) == flask.session["userid"])
    posts = db.getPosts(classid)
    return flask.render_template("class.html", className = classInfo[0],
		teacherName = db.getUserName(classInfo[1]), inviteCode = classInfo[2],
		weights = classInfo[3], classRoster = classRoster, getName = db.getUserName,
		isTeacher = isTeacher, classID = classid, posts = posts[::-1],
		getPostFiles = db.getPostFiles, desc = classInfo[3])

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
	if flask.session['userid'] != classInfo[1]:
		return "User is not the teacher of this class."
	classRoster = db.getRoster(classid)
	maxGrade,gradeDict = db.getAssignmentGrades(classid, assignment)
	return flask.render_template("gradebook.html", className = classInfo[0],
		assignment = assignment, roster = classRoster, gradeDict = gradeDict,
		getName = db.getUserName, classID = classid, maxGrade = maxGrade)

# =( how do these grades work?
@app.route('/submitGrades', methods = ["POST"])
def submitGrades():
	inputs = [None, None, None, None, None]
	for i in flask.request.form:
		print(i)
	try:
		inputs[0] = flask.request.form['classID']
		studentIDs = flask.request.form.getlist('studentID')
		studentGrades = flask.request.form.getlist('grade')
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
	classInfo = db.getClassInfo(inputs[0])
	if flask.session['userid'] != classInfo[1]:
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
	date = str(datetime.date.today())
	return flask.render_template("makepost.html", date=date, classID=classID)

@app.route('/processmakepost/<classID>', methods=['POST'])
def processMakePost(classID):
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
# we need to fix this.. png causes many many errors
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

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # can use http urls
    app.run(debug = True)

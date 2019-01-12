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

from requests_oauthlib import OAuth2Session

from urllib import request, parse
import sqlite3

from util import dbtools as db

app = flask.Flask(__name__)
app.secret_key = os.urandom(32)

with open("client_secret.json") as f:
	api_keys = json.load(f)

client_id = api_keys["web"]["client_id"]
client_secret = api_keys["web"]["client_secret"]
redirect_uri = "http://localhost:5000/oauth2callback"
auth_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
refresh_url = token_url
scope = [
    'https://www.googleapis.com/auth/calendar'
]

@app.route('/')
def index():
    return flask.render_template("login.html")
    #return ('<a href="/login"> Login with Google</a>')


@app.route('/login')
def login():
    if "credentials" not in flask.session:
        return flask.redirect("authorize")
    calendar = OAuth2Session(client_id, token=flask.session["credentials"])
    #entry = calendar.get("https://www.googleapis.com/calendar/v3/calendars/primary")
    entry = calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json()
    print(entry)

    userID = db.getUserID(entry["id"])

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

    #return flask.redirect("index.html")
    return flask.render_template("index.html", name = name, classnames = classNamesT, classids = classIDsT)

@app.route("/authorize")
def auth():
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(auth_base_url,
    access_type="offline", include_granted_scopes="true")
    flask.session["state"] = state
    return flask.redirect(authorization_url)

@app.route("/oauth2callback", methods=["GET"])
def callback():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, state=flask.session['state'])
    token = google.fetch_token(token_url, client_secret=client_secret, authorization_response=flask.request.url)
    flask.session["credentials"] = token
    return flask.redirect("/login")

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
        del flask.session['userid']
    return ('Credentials have been cleared.<br><br>')

@app.route('/regname', methods=["POST"])
def regname():
    name = flask.request.form['name']
    db.updateName(flask.session['userid'], name)
    return flask.redirect('/login')

@app.route('/makeclass')
def makeClass():
    return flask.render_template("makeclass.html")

@app.route('/processmakeclass', methods=['POST'])
def processMakeclass():
    classname = flask.request.form['classname']
    weightnames = flask.request.form.getlist('weightnames')
    weightnums = flask.request.form.getlist('weightnums')
    weightList = []
    for i in range(len(weightnames)):
        toAppend = [weightnames[i],weightnums[i]]
        weightList.append(toAppend)
    db.createClass(classname, flask.session["userid"], weightList)
    return flask.redirect("/login")

@app.route('/class/<classid>')
def classpage(classid):
    classInfo = db.getClassInfo(classid)
    classRoster = db.getRoster(classid)
    return flask.render_template("class.html", className = classInfo[0],
		teacherName = db.getUserName(classInfo[1]), inviteCode = classInfo[2],
		weights = classInfo[3], classRoster = classRoster, getName = db.getUserName)

@app.route('/invite/<inviteCode>')
def acceptInvite(inviteCode):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	result = db.acceptInvite(flask.session['userid'], inviteCode)
	return result

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

@app.route('/submitGrades', methods = ["POST"])
def submitGrades():
	inputs = [None, None, None, None]
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
	db.changeGrades(inputs[0], inputs[1], inputs[2], inputs[3])
	return "Grade update successful."

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug = True)

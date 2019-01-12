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

with open("keys/client_secret.json") as f:
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
    flask.session['userid'] = entry["etag"]

    try:
	    userInfo = db.getUserInfo(flask.session['userid'])
	    name = userInfo[0]
	    classNamesT = [i[1] for i in userInfo[2]] #List of names for classes being taught
	    classIDsT = [i[0] for i in userInfo[2]] #List of class IDs for classes being taught
	    classNamesE = [i[1] for i in userInfo[1]] #List of names for enrolled classes
	    classIDsE = [i[0] for i in userInfo[1]] #List of class IDs for enrolled classes
    except:
        db.registerUser(entry["etag"], entry["id"])
        return flask.render_template("register.html")

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
    # flash msg saying logout
    return (flask.redirect("/"))

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
    return flask.render_template("class.html", className = classInfo[0], teacherName = db.getUserName(classInfo[1]), inviteCode = classInfo[2], weights = classInfo[3])

@app.route('/invite/<inviteCode>')
def acceptInvite(inviteCode):
	if 'userid' not in flask.session:
		return flask.redirect('/')
	result = db.acceptInvite(flask.session['userid'], inviteCode)
	return result


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug = True)

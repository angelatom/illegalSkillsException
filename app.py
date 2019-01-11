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
    entry = flask.jsonify(calendar.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary').json())
    return entry
    #flask.session['userid'] = entry["id"] BROKE THIS
    

    with sqlite3.connect('classify.db') as db:
        c = db.cursor()
        try:
            c.execute("SELECT name FROM users WHERE userid='" + flask.session['userid'] + "';")
            name = c.fetchall()[0][0]
            c.execute("SELECT classname FROM classes where userid='" + flask.session['userid'] + "';")
            classnames = c.fetchall()
            print(classnames)
            c.execute("SELECT classid FROM classes where userid='" + flask.session['userid'] + "';")
            classids = c.fetchall()
        except:
            c.execute("INSERT INTO users VALUES ('" + entry["etag"] + "', '" + entry["id"] + "', '" + entry["id"] + "');")
            return flask.render_template("register.html")

    #return flask.redirect("index.html")
    return flask.render_template("index.html", name = name, classnames = classnames, classids = classids)

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
    with sqlite3.connect('classify.db') as db:
        c = db.cursor()
        c.execute("UPDATE users set name='" + name + "' WHERE userid='" + flask.session['userid'] + "';")
    return flask.redirect('/login')

@app.route('/makeclass')
def makeClass():
    return flask.render_template("makeclass.html")

@app.route('/processmakeclass', methods=['POST'])
def processMakeclass():
    classname = flask.request.form['classname']
    weightnames = flask.request.form.getlist('weightnames')
    weightnums = flask.request.form.getlist('weightnums')
    with sqlite3.connect('classify.db') as db:
        c = db.cursor()
        c.execute("SELECT classid FROM classes;")
        fetch = c.fetchall()
        try:
            classid = fetch[len(fetch) - 1][0] + 1
        except:
            classid = 0
        c.execute("INSERT INTO classes VALUES(" + str(classid) + ", '" + classname + "', '" + flask.session["userid"] + "');")
        for x in range(len(weightnames)):
            c.execute("INSERT INTO weights VALUES(" + str(classid) + ", '" + weightnames[x] + "', '" + weightnums[x] + "');")
    return flask.redirect("/login")

@app.route('/class/<classid>')
def classpage(classid):
    with sqlite3.connect('classify.db') as db:
        c = db.cursor()
        c.execute("SELECT * FROM classes where classid=" + classid + ";")
        classinfo = c.fetchall()
        c.execute("SELECT weightname FROM weights where classid=" + classid + ";")
        weightnames = c.fetchall()
        c.execute("SELECT weightvalue FROM weights where classid=" + classid + ";")
        weightnums = c.fetchall()
    return str(classinfo) + "<br>" + str(weightnames) + "<br>" + str(weightnums)

if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(debug = True)

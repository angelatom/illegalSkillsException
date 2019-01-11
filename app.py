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

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from urllib import request, parse
import sqlite3

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = os.urandom(32)


@app.route('/')
def index():
    return flask.render_template("login.html")
    #return ('<a href="/login"> Login with Google</a>')


@app.route('/login')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

  # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

    
    calendar = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    entry = calendar.calendars().get(calendarId='primary').execute()
    '''
    header={"Authorization": credentials.token}
    response = requests.get('https://www.googleapis.com/calendar/v3/users/me/calendarList/primary', headers = header)
    print(response)
    entry = response.json()
   '''
    flask.session['userid'] = entry["etag"]
  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

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


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.')
  else:
    return('An error occurred.')


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

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  if __name__ == "__main__":
    app.run(debug = True)

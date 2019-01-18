# Classify
## illegalSkillsException 
## Angela Tom, Kevin Lin, Aaron Li, Max Millar

## Overview:
Our website is a combination of Google Classroom elements and JupiterEd. This is basically a student management site/homework assignment site for teachers, and a grade site/homework submission site for students. Teachers will be able to create classes which students can join, and assign homework that students have to hand in either through a typed plain-text response or a file upload. Teachers can view, change, and add grades and notes for every student, and students can see them. Students and teachers can also send/receive messages.    

## Instructions to Run:
1. Go to root repository and click "Clone or Download"
2. Copy the ssh/https link and run ```$ git clone <link>```
3. Have the latest version of Python installed, which is currently Python 3.7.1.
4. Install virtualenv by running ```$ pip install virtualenv```
5. Make a venv by running ```$ python3 -m venv VENV_NAME```
* Activate it by running ```$ . ~/path_to_venv/VENV_NAME/bin/activate```
* Deactivate it by running ```$ deactivate```
6. Activate your virtual environment.
7. In the root of the directory, run ```$ pip install -r requirements.txt```
8. To obtain API keys, look below for the instructions.
9. Now you are ready to run the flask app. Run the command ```$ python app.py.``` (Make sure your virtual enviornment is actvated)
10. This should appear in the terminal after running the python file.   
```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 248-748-502
```
11. Open a web browser and navigate to the link http://localhost:5000/.

## Dependencies:
* Flask==1.0.2
```$ pip install Flask```
* Jinja2==2.10
```$ pip install Jinja2```
* google-api-python-client==1.7.7
```$ pip install google-api-python-client```
* google-auth==1.6.2
```$ pip install google-auth```
* google-auth-httplib2==0.0.3
```$ pip install google-auth-httplib2```


## API:
* Google calendar - Used to create events on the calendar based on teacher assignments
1. Head to https://console.developers.google.com/ to get a json file with client data (make sure to enable Calendar API)
2. Put client_secret.json in keys directory

* favQ - Used for random quotes on the site
1. Head to https://favqs.com/api to get an API key
2. Put quotes_key.txt in keys directory

* Adorable Avatars from http://avatars.adorable.io/

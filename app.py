'''
IllegalSkillsException
Aaron Li, Angela Tom, Kevin Lin, Max Millar
Softdev1 pd6
P#02 -- Final Project
2019-01-09
'''

import os
import json
import urllib

from flask import Flask, request, render_template, session, url_for, redirect, flash

# instantiate flask app
app = Flask(__name__)

# generate random key
app.secret_key = os.urandom(32)

@app.route("/")
def landing():
    return render_template("index.html")




# run flask app with debug set to true
if __name__ == "__main__":
    app.run(debug = True)

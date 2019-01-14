# Classify
## illegalSkillsException 
## Angela Tom, Kevin Lin, Aaron Li, Max Millar

## Overview:
Our website is a combination of Google Classroom elements and JupiterEd. This is basically a student management site/homework assignment site for teachers, and a grade site/homework submission site for students. Teachers will be able to create classes which students can join, and assign homework that students have to hand in either through a typed plain-text response or a file upload. Teachers can view, change, and add grades and notes for every student, and students can see them. Students and teachers can also send/receive messages.    

## Instructions to Run:
1. Open a terminal session.
2. Create your own virtual environment:
```
$ python3 -m venv virtual_env_name
```
3. Activate the virtual environment by typing ```$ . virtual_env_name/bin/activate``` in the terminal
4. Clone this repository. To clone this repo, open a terminal session and navigate to the directory you want for this repository to located in. Then clone using SSH by typing ```(venv)$ git@github.com:angelatom/illegalSkillsException.git```.
5. Navigate to the Smapify repository by typing ```$ cd illegalSkillsException/``` in the terminal.
6. Make sure you have all the dependencies installed in your virtual environment.
7. Procure API keys and place them into the keys folder.
8. Run the python file by typing ```(venv)$ python app.py``` in the terminal.
9. This should appear in the terminal after running the python file.   
```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 248-748-502
```

10. Open a web browser and navigate to the link http://localhost:5000/.

## Dependencies:
* Flask==1.0.2
* Jinja2==2.10

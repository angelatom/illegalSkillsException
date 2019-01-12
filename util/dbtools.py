import sqlite3, string, random

#These functions are meant to be ran from app.py, do not try to use them here.

def createClass(className, userID, weights):
    db,c = getDBCursor()
    c.execute("INSERT INTO classes (className, userID, invite) VALUES(?,?,?)", (className, userID, None,)) #Inserts row into classes table
    classID = -1
    for i in c.execute("SELECT classID FROM classes ORDER BY classID DESC LIMIT 1"): #Takes current classID
        classID = i[0]
    #Create an invite code by combining the classID and a random string of length six
    invite = str(classID) + ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
    c.execute("UPDATE classes SET invite = ? WHERE classID = ?", (invite, classID,)) #Adds the invite code to the row
    for i in weights: #Adds weights
        c.execute("INSERT INTO weights VALUES(?,?,?)", (classID, i[0], i[1]))
    closeDB(db)

def getClassInfo(classID):
    db,c = getDBCursor()
    #[className, userID, invite, [[weightName, weightValue]]]
    output = [None, None, None, None]
    for i in c.execute("SELECT className, userID, invite FROM classes WHERE classID = ?", (classID,)):
        for j in range(3):
            output[j] = i[j]
        weightList = []
        for j in c.execute("SELECT weightName, weightValue FROM weights WHERE classID = ?", (classID,)):
            weightInfo = [None, None] #[weightName, weightValue]
            for k in range(2):
                weightInfo[k] = j[k]
            weightList.append(weightInfo)
        output[3] = weightList
    closeDB(db)
    return output #Will be a tuple of None if no class of the classID inputted is found

def getUserName(userID):
    db,c = getDBCursor()
    name = None
    for i in c.execute("SELECT name FROM users WHERE userID = ?", (userID,)):
        name = i[0]
    closeDB(db)
    return name

def getUserInfo(userID):
    db,c = getDBCursor()
    enrolledClasses = []
    teachingClasses = []
    name = None
    for i in c.execute("SELECT name FROM users WHERE userID = ?", (userID,)):
        name = i[0]
    for i in c.execute("SELECT classID, className FROM classes WHERE userID = ?", (userID,)):
        someClass = [None, None] #[classID, className]
        for j in range(2):
            someClass[j] = i[j]
        teachingClasses.append(someClass)
    for i in c.execute("SELECT classID FROM roster WHERE userID = ?", (userID,)):
        someClass = [None, None] #[classID, className]
        someClass[0] = i[0]
        for j in c.execute("SELECT className FROM classes WHERE classID = ?", (i[0],)):
            someClass[1] = j[0]
        enrolledClasses.append(someClass)
    closeDB(db)
    return (name, enrolledClasses, teachingClasses)

def registerUser(email):
    db,c = getDBCursor()
    #Generate UUID
    numUsers = 0
    for i in c.execute("SELECT count(*) FROM users"):
        numUsers = i[0]
    userID = str(numUsers) + ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
    #Default name is the user's email
    c.execute("INSERT INTO users VALUES (?,?,?)", (userID, email, email))
    closeDB(db)
    return userID

def getUserID(email):
    db,c = getDBCursor()
    output = None
    for i in c.execute("SELECT userID FROM users WHERE email = ?", (email,)):
        output = i[0]
    closeDB(db)
    return output

def updateName(userID, name):
    db,c = getDBCursor()
    c.execute("UPDATE users SET name = ? WHERE userID = ?", (name, userID,))
    closeDB(db)

def acceptInvite(userID, inviteCode):
    db,c = getDBCursor()
    classID = None
    for i in c.execute("SELECT classID, userID FROM classes WHERE invite = ?", (inviteCode,)): #Check if the invite code exists
        classID = i[0]
        if i[1] == userID:
            return "User is the class instructor."
        break
    else:
        closeDB(db)
        return "Invite does not exist."
    for i in c.execute("SELECT * FROM roster WHERE classID = ? AND userID = ?", (classID, userID,)): #Check if the user is already enrolled
        closeDB(db)
        return "User already enrolled."
    c.execute("INSERT INTO roster VALUES (?,?)", (classID, userID,)) #Add user to the class roster
    closeDB(db)
    return "User enrolled."

def getRoster(classID):
    db,c = getDBCursor()
    output = []
    for i in c.execute("SELECT userID FROM roster WHERE classID = ?", (classID,)):
        output.append(i[0])
    closeDB(db)
    return output

def changeGrades(classID, gradeList, assignment, maxGrade):
    #gradeList [[userID, grade]]
    db,c = getDBCursor()
    for i in gradeList:
        for j in c.execute("SELECT userID FROM grades WHERE classID = ? AND userID = ? AND assignment = ?", (classID, i[0], assignment,)):
            #Grade already exists, so modify
            c.execute("UPDATE grades SET grade = ? WHERE classID = ? AND userID = ? AND assignment = ?", (grade, classID, i[0], assignment,))
            break
        else:
            #Otherwise create rows for grades
            c.execute("INSERT INTO grades VALUES (?,?,?,?,?)", (classID, i[0], assignment, i[1], maxGrade,))
    closeDB(db)

def getAssignmentGrades(classID, assignment):
    db,c = getDBCursor()
    output = {}
    maxGrade = ""
    for i in c.execute("SELECT maxGrade FROM grades WHERE classID = ? AND assignment = ? LIMIT 1", (classID, assignment,)):
        maxGrade = str(i[0])
    for i in c.execute("SELECT userID, grade FROM grades WHERE classID = ? AND assignment = ?", (classID, assignment,)):
        output[i[0]] = i[1] #output[userID] = gradeForUserID
    closeDB(db)
    return maxGrade,output

def getDBCursor():
    db = sqlite3.connect("data/classify.db")
    cursor = db.cursor()
    return db,cursor

def closeDB(db):
    db.commit()
    db.close()

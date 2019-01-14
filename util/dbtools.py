import sqlite3, string, random

#These functions are meant to be ran from app.py, do not try to use them here.

def createClass(className, userID, weights, desc):

    '''This function creates a class using the specified weights and teacher.
    '''

    db,c = getDBCursor()
    c.execute("INSERT INTO classes (className, userID, invite, desc) VALUES(?,?,?,?)", (className, userID, 'TEMP', desc,)) #Inserts row into classes table
    classID = -1
    for i in c.execute("SELECT classID FROM classes WHERE invite = ? LIMIT 1", ('TEMP',)): #Takes current classID
        classID = i[0]
    #Create an invite code by combining the classID and a random string of length six
    invite = str(classID) + ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
    c.execute("UPDATE classes SET invite = ? WHERE classID = ?", (invite, classID,)) #Adds the invite code to the row
    for i in weights: #Adds weights
        c.execute("INSERT INTO weights VALUES(?,?,?)", (classID, i[0], i[1]))
    closeDB(db)

def getClassInfo(classID):

    '''This function returns the name, teacher, invite code, and weights of a
       class as a list, with weights as another list of lists of length 2, with
       the first value as the name of the weight and the second as the value.
    '''

    db,c = getDBCursor()
    #[className, userID, invite, [[weightName, weightValue]], desc]
    output = [None, None, None, None, None]
    for i in c.execute("SELECT className, userID, invite, desc FROM classes WHERE classID = ?", (classID,)):
        for j in range(3):
            output[j] = i[j]
        output[4] = i[3]
        weightList = []
        for j in c.execute("SELECT weightName, weightValue FROM weights WHERE classID = ?", (classID,)):
            weightInfo = [None, None] #[weightName, weightValue]
            for k in range(2):
                weightInfo[k] = j[k]
            weightList.append(weightInfo)
        output[3] = weightList
    closeDB(db)
    return output #Will be a list of None if no class of the classID inputted is found

def getTeacher(classID):

    '''This function returns the userID of the teacher based on the classID
    '''

    db,c = getDBCursor()
    output = None
    for i in c.execute("SELECT userID FROM classes WHERE classID = ?", (classID,)):
        output = i[0]
    closeDB(db)
    return output

def getUserName(userID):

    '''This function returns the name of a user.
    '''

    db,c = getDBCursor()
    name = None
    for i in c.execute("SELECT name FROM users WHERE userID = ?", (userID,)):
        name = i[0]
    closeDB(db)
    return name

def getUserInfo(userID):

    '''This function returns the name, enrolled classes, and classes that a user
       teaches. Classes are returned as a list of lists of length 3, with the
       first value as the class ID, the second the name of the class, and the
       third its description.
    '''

    db,c = getDBCursor()
    enrolledClasses = []
    teachingClasses = []
    name = None
    for i in c.execute("SELECT name FROM users WHERE userID = ?", (userID,)):
        name = i[0]
    for i in c.execute("SELECT classID, className, desc FROM classes WHERE userID = ?", (userID,)):
        someClass = [None, None, None] #[classID, className, desc]
        for j in range(3):
            someClass[j] = i[j]
        teachingClasses.append(someClass)
    for i in c.execute("SELECT classID FROM roster WHERE userID = ?", (userID,)):
        someClass = [None, None, None] #[classID, className, desc]
        someClass[0] = i[0]
        for j in c.execute("SELECT className, desc FROM classes WHERE classID = ?", (i[0],)):
            someClass[1] = j[0]
            someClass[2] = j[1]
        enrolledClasses.append(someClass)
    closeDB(db)
    return (name, enrolledClasses, teachingClasses)

def registerUser(email):

    '''This function registers a user and returns a unique user ID.
    '''

    db,c = getDBCursor()
    #Default name is the user's email
    c.execute("INSERT INTO users VALUES (?,?,?)", ('TEMP', email, email))
    #Generate UUID
    rowID = -1
    for i in c.execute("SELECT ROWID FROM users WHERE userID = ?", ('TEMP',)):
        numUsers = i[0]
    userID = str(numUsers) + ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
    c.execute("UPDATE users SET userID = ? WHERE userID = ?", (userID,'TEMP',))
    closeDB(db)
    return userID

def getUserID(email):

    '''This function returns the userID of a user with the given email. Returns
       None if the user does not exist.
    '''

    db,c = getDBCursor()
    output = None
    for i in c.execute("SELECT userID FROM users WHERE email = ?", (email,)):
        output = i[0]
    closeDB(db)
    return output

def updateName(userID, name):

    '''This function sets the name of a user.
    '''

    db,c = getDBCursor()
    c.execute("UPDATE users SET name = ? WHERE userID = ?", (name, userID,))
    closeDB(db)

def acceptInvite(userID, inviteCode):

    '''This function adds a user to the roster of a class if the invite code
       exists. Returns a string regarding the status of the invite acceptance.

    PREREQ: userID exists
    '''

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

    '''This function returns a list of the users enrolled in a class.
    '''

    db,c = getDBCursor()
    output = []
    for i in c.execute("SELECT userID FROM roster WHERE classID = ?", (classID,)):
        output.append(i[0])
    closeDB(db)
    return output

def changeGrades(classID, gradeList, assignment, maxGrade):

    '''This function updates the grades of the given assignment for a class.
       gradeList should be a list with each element [userID, grade].
    '''

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

    '''This function returns the max grade and current grades of students for
       an assignment.
    '''

    db,c = getDBCursor()
    output = {}
    maxGrade = ""
    for i in c.execute("SELECT maxGrade FROM grades WHERE classID = ? AND assignment = ? LIMIT 1", (classID, assignment,)):
        maxGrade = str(i[0])
    for i in c.execute("SELECT userID, grade FROM grades WHERE classID = ? AND assignment = ?", (classID, assignment,)):
        output[i[0]] = i[1] #output[userID] = gradeForUserID
    closeDB(db)
    return maxGrade,output

def getClassID(postID):

    '''This function returns the classID associated with a postID.
    '''

    db,c = getDBCursor()
    output = None
    for i in c.execute("SELECT classID FROM posts WHERE postID = ? LIMIT 1", (postID,)):
        output = i[0]
    closeDB(db)
    return output

def isEnrolled(userID, classID):

    '''This function returns a boolean based on if the given user is enrolled in
       the given class.
    '''

    db,c = getDBCursor()
    output = False
    for i in c.execute('SELECT * FROM roster WHERE classID = ? AND userID = ?', (classID, userID,)):
        output = True
    closeDB(db)
    return output

def addFile(postID, userID):

    '''This function registers a file given by a user from a post. If the user
       has already submitted a file to this post, the function will return the
       old file name, otherwise, it will generate and return a new name.
    '''

    db,c = getDBCursor()
    filename = None
    for i in c.execute('SELECT filename FROM files WHERE postID = ? AND userID = ?', (postID, userID,)): #Check if file already exists
        filename = i[0]
    if filename == None: #Generate new file name if it doesn't exist
        c.execute('INSERT INTO files (postID, filename, userID) VALUES (?,?,?)', (postID, 'TEMP', userID))
        rowID = 0
        for i in c.execute("SELECT ROWID FROM files WHERE filename = ?", ('TEMP',)):
            rowID = i[0]
        filename = str(rowID) + ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(6))
        c.execute("UPDATE files SET filename = ? WHERE filename = ?", (filename,'TEMP',))
    c.execute("UPDATE files SET submission = CURRENT_TIMESTAMP WHERE filename = ?", (filename,)) #Updates submission timestamp
    closeDB(db)
    return filename

def makePost(classID, dueDate, postBody, submittable):

    '''This function creates a post based on teacher input. It creates the
       postID and submissionDate.
    '''

    db,c = getDBCursor()
    c.execute("INSERT INTO posts (classID, duedate, postBody, submittable) VALUES(?,?,?,?)", (-1, dueDate, postBody, submittable)) #Inserts row into posts table
    postID = -1
    for i in c.execute("SELECT ROWID FROM posts WHERE classID = ? LIMIT 1", (-1,)): #Takes current postID
        postID = i[0]
    c.execute("UPDATE posts SET submission = CURRENT_TIMESTAMP, classID = ? WHERE postID = ?", (classID, postID,)) #Adds the submission to the row
    closeDB(db)

def getPosts(classID):

    '''This function returns all of the posts when given a classID.
    '''

    db,c = getDBCursor()
    c.execute("SELECT * FROM posts WHERE classID = ? ORDER BY submission", (classID,))
    output = c.fetchall()
    closeDB(db)
    return output

def fileExists(filename):

    '''This function returns True if the file is in the database, and False
       otherwise.
    '''

    db,c = getDBCursor()
    output = False
    for i in c.execute("SELECT * FROM files WHERE fileName = ?", (filename,)):
        output = True
    closeDB(db)
    return output

def getPostFiles(postID):

    '''This function returns a list of lists containing student upload
       information on a specific post.
    '''

    db,c = getDBCursor()
    output = []
    for i in c.execute("SELECT filename, userID, submission FROM files WHERE postID = ?", (postID,)):
        toAppend = [None,None,None] #[filename, userID, timestamp]
        for j in range(3):
            toAppend[j] = i[j]
        output.append(toAppend)
    closeDB(db)
    return output

def getDBCursor():
    db = sqlite3.connect("data/classify.db")
    cursor = db.cursor()
    return db,cursor

def closeDB(db):
    db.commit()
    db.close()

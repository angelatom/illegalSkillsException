import sqlite3

DB_FILE="../data/classify.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

def createTable():
    c.execute("CREATE TABLE IF NOT EXISTS users(userID TEXT PRIMARY KEY, email TEXT, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS classes(classID INTEGER PRIMARY KEY, className TEXT, userID TEXT, invite TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS weights(classID INTEGER, weightName TEXT, weightValue DECIMAL)")
    c.execute("CREATE TABLE IF NOT EXISTS roster(classID INTEGER, userID TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS grades(classID INTEGER, userID TEXT, assignment TEXT, grade INTEGER, maxGrade INTEGER, weight TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts(postID INTEGER PRIMARY KEY, classID INTEGER, submission DATETIME, duedate DATETIME, postBody TEXT, submittable INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS files(postID INTEGER, filename TEXT, userID TEXT, submission DATETIME)")

createTable()

db.commit()
db.close()

import sqlite3

DB_FILE="classify.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

def createTable():
    c.execute("CREATE TABLE users(userid TEXT PRIMARY KEY, email TEXT, name TEXT)")
    c.execute("CREATE TABLE classes(classid INTEGER PRIMARY KEY, classname TEXT, userid TEXT)")
    c.execute("CREATE TABLE weights(classid INTEGER, weightname TEXT, weightvalue DECIMAL)")

createTable()

db.commit()
db.close()

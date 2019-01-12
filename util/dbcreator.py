import sqlite3

DB_FILE="../data/classify.db"

db = sqlite3.connect(DB_FILE)
c = db.cursor()

def createTable():
    c.execute("CREATE TABLE IF NOT EXISTS users(userID TEXT PRIMARY KEY, email TEXT, name TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS classes(classID INTEGER PRIMARY KEY, className TEXT, userID TEXT, invite TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS weights(classID INTEGER, weightName TEXT, weightValue DECIMAL)")
    c.execute("CREATE TABLE IF NOT EXISTS roster(classID INTEGER, userID TEXT)")

createTable()

db.commit()
db.close()

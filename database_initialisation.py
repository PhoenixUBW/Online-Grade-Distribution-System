# Importing sqlite3 to create the tables
import sqlite3

# Create user database table
def create_user_db():
    with sqlite3.connect("users.db") as con:
        c = con.cursor()
        c.execute("CREATE TABLE users (ID INTEGER, name TEXT, hashed_passphrase TEXT, account_type TEXT, class_code TEXT)")

# Create student grades database table
def create_grades_db():
    with sqlite3.connect("grades.db") as con:
        c = con.cursor()
        c.execute("CREATE TABLE grades (ID INTEGER, subject TEXT, grade TEXT, date_updated TEXT)")

# If this file is ran independantly it will create the tables (e.g. I run the file myself)
# However when this file is imported into another the functions will not run until called in that file
if __name__ == "__main__":
    create_user_db()
    create_grades_db()
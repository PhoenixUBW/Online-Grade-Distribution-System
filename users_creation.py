import sqlite3
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

#commented out 3 example users - 1 teacher, 2 students (1 in the teachers class, 1 in a different class)

key = b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54='
crypter = Fernet(key)

def create_db(crypter):
    with sqlite3.connect("users.db") as con:
        c = con.cursor()
        c.execute("CREATE TABLE users (ID TEXT, name TEXT, hashed_passphrase TEXT, account_type TEXT, class_code TEXT, grade TEXT, date_grade TEXT)")
        #c.execute("INSERT INTO users VALUES('1', ?, ?, 'student', 'C1', ?, ?)",(crypter.encrypt(b"John"), generate_password_hash("Password_12345"),crypter.encrypt(b"NONE"),crypter.encrypt(b"NONE")))
        #c.execute("INSERT INTO users VALUES('2', ?, ?, 'student', 'C2', ?, ?)",(crypter.encrypt(b"Sam"), generate_password_hash("Password_12345"),crypter.encrypt(b"NONE"),crypter.encrypt(b"NONE")))
        #c.execute("INSERT INTO users VALUES('3', ?, ?, 'teacher', 'C1', ?, ?)",(crypter.encrypt(b"Jake"), generate_password_hash("Password_12345"),crypter.encrypt(b"NONE"),crypter.encrypt(b"NONE")))
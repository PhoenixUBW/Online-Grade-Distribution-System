import sqlite3
from cryptography.fernet import Fernet

key = b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54='
crypter = Fernet(key)

with sqlite3.connect("grades.db") as con:
    c = con.cursor()
    c.execute("SELECT subject ,grade, date FROM grades WHERE ID=1")
    subjects = []
    grades = []
    dates = []
    fetch = c.fetchall()
    for row in fetch:
        subjects.append(crypter.decrypt(row[0]).decode("UTF-8"))
        grades.append(crypter.decrypt(row[1]).decode("UTF-8"))
        dates.append(crypter.decrypt(row[2]).decode("UTF-8"))

print(subjects)
print(grades)
print(dates)

# [(b'gAAAAABjmyEuWxH9NNr-...XN5Z3YAw==', b'gAAAAABjmyEuiw2ntnSO...m6pFRzHg==', b'gAAAAABjmyEuvQUgUdJs...DGfT_jtA=='),
#  (b'gAAAAABjmyEuJJOymP3R...MATVdalA==', b'gAAAAABjmyEuBjFaAY4z...DZrvy73Q==', b'gAAAAABjmyEue8NnvFje...qSXrW65Q==')]
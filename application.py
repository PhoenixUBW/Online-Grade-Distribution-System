from flask import Flask, session, flash, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os.path
import sqlite3
from datetime import date
from database_initialisation import create_user_db, create_grades_db
from config import DevConfig, ProductionConfig

#wtforms, sqlalchemy, django, postgreSQL, bcrypt

#TO-DO - database initialisation uses config rather than hardcoded key,multiple subjects, multiple grades, uses stacks to make forwards and back buttons, settings, change grade db to student info db, securely kept keys
#teacher's comments?, attendance, behaviour, predicted grade, more modular update pages/functions, encrypted class codes and account types?, locks you out for time after failed attemps

#working but subject doesnt actually get updated

app = Flask(__name__)

config = DevConfig()

app.secret_key = config.get_SECRET_KEY()

crypter = Fernet(config.get_EN_KEY())

VALID_GRADES = ["","A*","A","B","C","D","E","F"]
SYMBOLS = ["`","!",'"',"'","$","%","^","&","*","(",")","-","_","+","=","[","]","{","}","|",";",":","@","~","#",",","<",">",".","?","/"]
NUMBERS = ["0","1","2","3","4","5","6","7","8","9"]
ALPHABET = [" ","a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
           "z","A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

if os.path.exists(config.get_USER_DB()) == False:
    create_user_db(crypter)
if os.path.exists(config.get_GRADES_DB()) == False:
    create_grades_db(crypter)

def valid_ID(data):
    error = None
    if data == "":
        error = "No ID inputted"
        return False, error
    for char in data:
        if char not in NUMBERS:
            error = "IDs must only contain numbers"
            return False, error
    return True, error

def valid_name(data):
    error =  None
    for char in data:
        if char not in ALPHABET:
            error = "Names must only contain letters"
            return False, error
    if len(data) < 2:
        error = "Names must be greater than 1 character"
        return False, error
    return True, error

def valid_passphrase(data):
    error = None
    alpha = False
    num = False
    sym = False
    length = False
    for char in data:
        if char in ALPHABET:
            alpha = True
        if char in NUMBERS:
            num = True
        if char in SYMBOLS:
            sym = True
    if len(data) > 11:
        length = True
    else:
        error = "Passphrase must be greater than 11 characters"
    if alpha == False:
        error = "Passphrase has no alphabetic letters"
    if num == False:
        error = "Passphrase has no numbers"
    if sym == False:
        error = "Passphrase has no symbols"
    if alpha == True and num == True and sym == True and length == True:
        return True, error
    else:
        return False, error

def valid_account_type(data):
    error = None
    if data != "Student" and data != "Teacher":
        error = "Account type must = 'Student' or 'Teacher'"
        return False, error
    return True, error

def valid_class_code(data):
    error = None
    if data == "":
        error = "No class code inputted "
        return False, error
    for char in data:
        if char not in ALPHABET and char not in NUMBERS:
            error = "Class code must only contain alphabetic and numeric characters"
            return False, error
    return True, error

def valid_grade(data):
    error = None
    if data not in VALID_GRADES:
        error = "Grade must be in our set of valid grades"
        return False, error
    return True, error

def list_ID():
    with sqlite3.connect(config.get_USER_DB()) as con: 
        c = con.cursor()
        c.execute("SELECT ID FROM users")
        temp = c.fetchall()
    IDs = list()
    for ID in temp:
        IDs.append(str(ID[0]))
    return IDs

def user_required(ID):
    if "ID" in session:
        var1 = session["ID"]
        var2 = ID
        if session["ID"] == ID:
            return True
        else:
            flash("You are not logged in as the required user to view this page")
            return False
    else:
        flash("You must be logged in to view this page")
        return False

class Student():
    def __init__(self,ID):
        with sqlite3.connect(config.get_GRADES_DB()) as con:
            c = con.cursor()
            c.execute("SELECT subject ,grade, date_updated FROM grades WHERE ID=?",(ID,))
            subjects = []
            grades = []
            dates = []
            fetch = c.fetchall()
            for row in fetch:
                subjects.append(row[0])
                grades.append(crypter.decrypt(row[1]).decode("UTF-8"))
                dates.append(crypter.decrypt(row[2]).decode("UTF-8"))
        num_subjects = []
        for x in range(0,len(subjects)):
            num_subjects.append(x)
        self.__subjects = subjects
        self.__grades = grades
        self.__dates = dates
        self.__num_subjects = num_subjects

    def get_subjects(self):
        return self.__subjects

    def get_grades(self):
        return self.__grades

    def get_dates(self):
        return self.__dates
    
    def get_num_subjects(self):
        return self.__num_subjects

class Teacher():
    def __init__(self,target):
        self.__target = target
    def update_grade(self,newgrade,subject): 
        with sqlite3.connect(config.get_GRADES_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE grades SET grade=?, date_updated=? WHERE ID=? AND WHERE grade=?",(crypter.encrypt(bytes(newgrade, "utf-8")), crypter.encrypt(bytes(str(date.today()), "utf-8")), self.__target, subject))

class Admin():
    def __init__(self,target):
        self.__target = target
    def update_name(self,newname):
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET name=? WHERE ID=?",(crypter.encrypt(bytes(newname, "utf-8")), self.__target))

    def update_passphrase(self, newpassphrase):
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET hashed_passphrase=? WHERE ID=?",(generate_password_hash(newpassphrase), self.__target))

    def update_class_code(self, newclass_code):
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET class_code=? WHERE ID=?",(newclass_code, self.__target))

    def delete(self):
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("DELETE FROM users WHERE ID=?",(self.__target,))

class User():
    def __init__(self,ID):
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("SELECT * FROM users WHERE ID=?",(ID,))
            info = c.fetchall()[0]
        self.__ID = info[0]
        self.__name = crypter.decrypt(info[1]).decode("UTF-8")
        self.__hashed_passphrase = info[2]
        self.__passphrase = "unavailable"
        self.__account_type = info[3]
        self.__class_code = info[4]
        if "ID" in session:
            if self.__account_type == "Student":
                self.student = Student(ID)
            if session["account_type"] == "Teacher":
                self.teacher = Teacher(ID)
            if session["ID"] == config.get_ADMIN_USERNAME():
                self.admin = Admin(ID)

    def get_ID(self):
        return self.__ID
    
    def get_name(self):
        return self.__name

    def get_hashed_passphrase(self):
        return self.__hashed_passphrase
    
    def get_passphrase(self):
        return self.__passphrase

    def get_account_type(self):
        return self.__account_type

    def get_class_code(self):
        return self.__class_code

def logged_in():
    if "ID" in session:
        if session["ID"] == "admin":
            return "Logged in as: Admin"
        else:
            user=User(session["ID"])
            return f"Logged in as: {user.get_name()}"
    else:
        return "Login"
    
@app.errorhandler(404)
def not_found(error_number):
    return render_template("404.html", logged_in=logged_in())

@app.route("/")
def homepage():
    error = None
    return render_template("homepage.html", error=error, logged_in=logged_in())

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["ID"] == config.get_ADMIN_USERNAME() and request.form["passphrase"] == config.get_ADMIN_PASSPHRASE():
            session["ID"] = config.get_ADMIN_USERNAME()
            return redirect(url_for("admin_homepage"))
        IDs = list_ID()
        if valid_ID(request.form["ID"])[0] == True and request.form["ID"] in IDs:
            user = User(request.form["ID"])
            if valid_passphrase(request.form["passphrase"])[0] == True and check_password_hash(user.get_hashed_passphrase(),request.form["passphrase"]) == True: #ERROR HERE, fix using breakpoints, will just be small inconsistency
                session["ID"] = str(user.get_ID())
                session["account_type"] = user.get_account_type()
                flash("You have succesfully been logged in")                
                if user.get_account_type() == "Student":
                    return redirect(f"/student/{user.get_ID()}")
                elif user.get_account_type() == "Teacher":
                    return redirect(f"/teacher/{user.get_ID()}")
            else:
                error = "Invalid passphrase"
        else:
            error = "Invalid ID"
    return render_template("login.html", error=error, logged_in=logged_in())

@app.route("/student/<student_ID>")
def student_homepage(student_ID):
    error = None
    if user_required(student_ID) == True:
        student = User(student_ID)
    else:
        return redirect(url_for("login"))
    return render_template("student_homepage.html", student=student, error=error, logged_in=logged_in())

@app.route("/teacher/<teacher_ID>")
def teacher_homepage(teacher_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type=? AND class_code=?",("Student",teacher.get_class_code()))
            lt_students = c.fetchall()
            students = list()
            for student in lt_students:
                students.append(User(student[0]))
    else:
        return redirect(url_for("login"))

    return render_template("teacher_homepage.html",students=students, teacher=teacher, error=error, logged_in=logged_in()) 

@app.route("/teacher/<teacher_ID>/update_grade/<student_ID>/<subject_index>", methods=["GET","POST"])
def teacher_update_grade(teacher_ID,student_ID,subject_index):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        student = User(student_ID)
        if teacher.get_class_code() == student.get_class_code():
            if request.method == "POST":
                if valid_grade(request.form["grade"])[0] == True:
                    if check_password_hash(teacher.get_hashed_passphrase(), request.form["passphrase"]) == True:
                        student.teacher.update_grade(request.form["grade"],student.student.get_subjects()[subject_index]) #not updating
                        flash("Grade successfully updated")
                    else:
                        error = "Incorrect password "
                else:
                    error = valid_grade(request.form["grade"])[1]
        else:
            error = "This student is not in your class "
    else:
        return redirect(url_for("login"))
    return render_template("teacher_update_grade.html", student=student, teacher=teacher, error=error, logged_in=logged_in(), subject_index=int(subject_index))

@app.route("/admin")
def admin_homepage():
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True:
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type='Student' OR account_type='Teacher'")
            lt_users = c.fetchall()
            users = list()
            for user in lt_users:
                users.append(User(user[0]))
    else:
        return redirect(url_for("login"))
    return render_template("admin_homepage.html", users=users, error=error, logged_in=logged_in())

@app.route("/admin/update_name/<user_ID>", methods=["GET","POST"])
def update_name(user_ID):
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_name(request.form["attribute"])[0] == True:
                if request.form["attribute"] == request.form["confirm_attribute"]:
                    if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                        user.admin.update_name(request.form["attribute"])
                        flash("Name succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_name(request.form["attribute"])[1]
    else:
        return redirect(url_for("admin"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_name(), attribute="Name", type = "text", error=error, logged_in=logged_in())

@app.route("/admin/update_passphrase/<user_ID>", methods=["GET","POST"])
def update_passphrase(user_ID): 
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_passphrase(request.form["attribute"])[0] == True:
                if request.form["attribute"] == request.form["confirm_attribute"]:
                    if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                        user.admin.update_passphrase(request.form["attribute"])
                        flash("Passphrase succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_passphrase(request.form["attribute"])[1]
    else:
        return redirect(url_for("login"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_passphrase(), attribute="Passphrase", type = "password",error=error, logged_in=logged_in())

@app.route("/admin/update_class_code/<user_ID>", methods=["GET","POST"])
def update_class_code(user_ID):
    error = ""
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_class_code(request.form["attribute"])[0] == True:
                if request.form["attribute"] == request.form["confirm_attribute"]:
                    if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                        user.admin.update_class_code(request.form["attribute"])
                        flash("Class code succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_class_code(request.form["attribute"])[1]
    else:
        return redirect(url_for("login"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_class_code(), attribute="Class Code", type = "text", error=error, logged_in=logged_in())

@app.route("/admin/create_user", methods=["GET","POST"])
def create_user():
    error = ""
    if user_required(config.get_ADMIN_USERNAME()) == True:
        valid_user = True
        if request.method == "POST":
            IDs = list_ID()
            if request.form["ID"] in IDs:
                valid_user = False
                error = "There is already an existing user with this ID "
            if valid_ID(request.form["ID"])[0] == False:
                valid_user = False
                error = valid_ID(request.form["ID"])[1]
            if valid_name(request.form["name"])[0] == False:
                valid_user = False
                error + valid_name(request.form["name"])[1]
            if valid_passphrase(request.form["passphrase"])[0] == False:
                valid_user = False
                error = valid_passphrase(request.form["passphrase"])[1]
            if valid_account_type(request.form["account_type"])[0] == False:
                valid_user = False
                error = valid_account_type(request.form["account_type"])[1]
            if valid_class_code(request.form["class_code"])[0] == False:
                valid_user = False
                error = valid_class_code(request.form["class_code"])[1]
            if valid_user == True:
                if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                    with sqlite3.connect(config.get_USER_DB()) as con:
                        c = con.cursor()
                        c.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?)",
                                  (request.form["ID"],
                                  crypter.encrypt(bytes(request.form["name"], "utf-8")),
                                  generate_password_hash(request.form["passphrase"]),
                                  request.form["account_type"],
                                  request.form["class_code"]))
                    if request.form["account_type"] == "Student":
                        with sqlite3.connect(config.get_grades_DB()) as con:
                            c = con.cursor()
                            c.execute("INSERT INTO grades VALUES(?,'NONE','NONE')",(request.form["ID"],))
                    flash("User successfully added")
                else:
                    error = "Incorrect passphrase "
    else:
        return redirect(url_for("login"))
    return render_template("admin_create_user.html", error=error, logged_in=logged_in())

@app.route("/admin/delete_user/<user_ID>", methods=["GET","POST"])
def delete_user(user_ID):
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if request.form["passphrase"] == config.get_ADMIN_PASSPHRASE():
                user.admin.delete()
                flash("User successfully deleted")
                return redirect(url_for("admin_homepage"))
            else:
                error = "Incorrect passphrase"
    else:
        return redirect(url_for("login"))
    return render_template("admin_delete_user.html", error=error, user_ID=user_ID, logged_in=logged_in())

@app.route("/logout")
def logout():
    if "ID" in session:
        session.pop("ID",None)
        flash("You have been logged out")
    else:
        flash("You are not logged in")
    return redirect(url_for("login"))

@app.route("/current_user/<previous_url>")
def current_user(previous_url):
    if "ID" in session:
        flash(f"ID: {session['ID']} is logged in")
    else:
        flash("No user is logged in")
    return redirect(url_for(previous_url))

@app.route("/input_requirements")
def input_requirements():
    return render_template("input_requirements.html", grades=VALID_GRADES, letters=ALPHABET, numbers=NUMBERS, symbols=SYMBOLS, logged_in=logged_in())

@app.route("/test")
def test():
    return render_template("test.html",list=[1,2,3,4,5])

if __name__ == "__main__":
    app.run(debug=config.get_DEBUG())
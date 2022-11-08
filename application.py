from flask import Flask, session, flash, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os.path
import sqlite3
from datetime import date
from users_creation import create_db
from config import DevConfig, ProductionConfig

#wtforms, sqlalchemy, django, postgreSQL, bcrypt, 
#private and protected classes, getter and setters - change how my objects work - , class inheritance, User - student/teacher

#why in vscode does the running crash everytime I make a change

#TO-DO - css/make it look good, securely kept keys
#teacher's comments?, more modular update pages/functions, store grades seperate to user.db?, encrypted class codes and account types?, locks you out for time after failed attemps?

app = Flask(__name__)

config = DevConfig()

app.secret_key = config.SECRET_KEY #make key safe

crypter = Fernet(config.EN_KEY)

VALID_GRADES = ["","A*","A","B","C","D","E","F"]
SYMBOLS = ["`","!",'"',"'","$","%","^","&","*","(",")","-","_","+","=","[","]","{","}","|",";",":","@","~","#",",","<",">",".","?","/"]
NUMBERS = ["0","1","2","3","4","5","6","7","8","9"]
ALPHABET = [" ","a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
           "z","A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

if os.path.exists(config.DB) == False:
    create_db(crypter) 

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
    if data != "student" and data != "teacher":
        error = "Account type must = 'student' or 'teacher'"
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
    with sqlite3.connect(config.DB) as con: 
        c = con.cursor()
        c.execute("SELECT ID FROM users")
        temp = c.fetchall()
    IDs = list()
    for ID in temp:
        IDs.append(ID[0])
    return IDs

def user_required(user_name):
    if "ID" in session:
        if session["ID"] == user_name:
            return True
        else:
            flash("You are not logged in as the required user to view this page")
            return False
    else:
        flash("You must be logged in to view this page")
        return False

class User():
    def __init__(self,ID):
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("SELECT * FROM users WHERE ID=?",(ID,)) #gets all info for that user
            info = c.fetchall()[0]
        self.__ID = info[0]
        self.__name = crypter.decrypt(info[1]).decode("UTF-8")
        self.__hashed_passphrase = info[2]
        self.__passphrase = "unavailable"
        self.__account_type = info[3]
        self.__class_code = info[4]
        self.__grade = crypter.decrypt(info[5]).decode("UTF-8")
        self.__date_grade = crypter.decrypt(info[6]).decode("UTF-8")

    def get_ID(self):
        return self.__ID #object_name.attribute
    
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

    def get_grade(self):
        return self.__grade

    def get_date_grade(self):
        return self.__date_grade

    def update_name(self,newname): #updaters are the setter methods (only difference is the values have initialised values and then can be set to be other things/or updated)
        self.__name = newname
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("UPDATE users SET name=? WHERE ID=?",(crypter.encrypt(bytes(self.__name, "utf-8")), self.ID))

    def update_passphrase(self, newpassphrase):
        self.__hashed_passphrase = generate_password_hash(newpassphrase)
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("UPDATE users SET hashed_passphrase=? WHERE ID=?",(self.__hashed_passphrase, self.ID))

    def update_class_code(self, newclass_code):
        self.__class_code = newclass_code
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("UPDATE users SET class_code=? WHERE ID=?",(self.__class_code, self.ID))

    def update_grade(self,newgrade):
        self.__grade = newgrade
        self.__date_grade = date.today()
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("UPDATE users SET grade=?, date_grade=? WHERE ID=?",(crypter.encrypt(bytes(self.__grade, "utf-8")), crypter.encrypt(bytes(str(self.__date_grade), "utf-8")), self.__ID))

    def delete(self):
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("DELETE FROM users WHERE ID=?",(self.__ID,))
    
@app.errorhandler(404)
def not_found(error_number):
    return render_template("404.html")

@app.route("/")
def homepage():
    error = None
    return render_template("homepage.html", error=error)

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["ID"] == "admin" and request.form["passphrase"] == config.ADMIN_PASSPHRASE:
            session["ID"] = "admin"
            return redirect(url_for("admin_homepage"))
        IDs = list_ID()
        if valid_ID(request.form["ID"])[0] == True and request.form["ID"] in IDs:
            user = User(request.form["ID"])
            if valid_passphrase(request.form["passphrase"])[0] == True and check_password_hash(user.get_hashed_passphrase(),request.form["passphrase"]) == True:
                session["ID"] = user.get_ID()
                flash("You have succesfully been logged in")                
                if user.get_account_type() == "student":
                    return redirect(f"/student/{user.get_ID()}")
                elif user.get_account_type() == "teacher":
                    return redirect(f"/teacher/{user.get_ID()}")
            else:
                error = "Invalid passphrase"
        else:
            error = "Invalid ID"
    return render_template("login.html", error=error)

@app.route("/teacher/<teacher_ID>")
def teacher_homepage(teacher_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type=? AND class_code=?",("student",teacher.get_class_code()))
            lt_students = c.fetchall()
            students = list()
            for student in lt_students:
                students.append(User(student[0]))
    else:
        return redirect(url_for("login"))
    return render_template("teacher_homepage.html",students=students, teacher=teacher, error=error) 

@app.route("/teacher/<teacher_ID>/update_grade/<student_ID>", methods=["GET","POST"])
def teacher_update_grade(teacher_ID,student_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        student = User(student_ID)
        if student.get_class_code() == teacher.get_class_code():
            if request.method == "POST":
                if valid_grade(request.form["grade"])[0] == True:
                    if check_password_hash(teacher.get_hashed_passphrase(), request.form["passphrase"]) == True:
                        student.update_grade(request.form["grade"])
                        flash("Grade successfully updated")
                    else:
                        error = "Incorrect password "
                else:
                    error = valid_grade(request.form["grade"])[1]
        else:
            error = "This student is not in your class "
    else:
        return redirect(url_for("login"))
    return render_template("teacher_update_grade.html", student=student, teacher=teacher, error=error)

@app.route("/student/<student_ID>")
def student_homepage(student_ID):
    error = None
    if user_required(student_ID) == True:
        student = User(student_ID)
    else:
        return redirect(url_for("login"))
    return render_template("student_homepage.html", student=student, error=error)

@app.route("/admin")
def admin_homepage():
    error = None
    if user_required("admin") == True:
        with sqlite3.connect(config.DB) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type='student' OR account_type='teacher'")
            lt_users = c.fetchall()
            users = list()
            for user in lt_users:
                users.append(User(user[0]))
    else:
        return redirect(url_for("login"))
    return render_template("admin_homepage.html", users=users, error=error)

@app.route("/admin/update_name/<user_ID>", methods=["GET","POST"])
def update_name(user_ID):
    error = None
    if user_required("admin") == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_name(request.form["name"])[0] == True:
                if request.form["name"] == request.form["confirm_name"]:
                    if request.form["admin_passphrase"] == config.ADMIN_PASSPHRASE:
                        user.update_name(request.form["name"])
                        flash("Name succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_name(request.form["name"])[1]
    else:
        return redirect(url_for("admin"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_name(), attribute="name", type = "text", error=error)

@app.route("/admin/update_passphrase/<user_ID>", methods=["GET","POST"])
def update_passphrase(user_ID): 
    error = None
    if user_required("admin") == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_passphrase(request.form["passphrase"])[0] == True:
                if request.form["passphrase"] == request.form["confirm_passphrase"]:
                    if request.form["admin_passphrase"] == config.ADMIN_PASSPHRASE:
                        user.update_passphrase(request.form["passphrase"])
                        flash("Passphrase succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_passphrase(request.form["passphrase"])[1]
    else:
        return redirect(url_for("login"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_passphrase(), attribute="passphrase", type = "password",error=error)

@app.route("/admin/update_class_code/<user_ID>", methods=["GET","POST"])
def update_class_code(user_ID):
    error = ""
    if user_required("admin") == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_class_code(request.form["class_code"])[0] == True:
                if request.form["class_code"] == request.form["confirm_class_code"]:
                    if request.form["admin_passphrase"] == config.ADMIN_PASSPHRASE:
                        user.update_class_code(request.form["class_code"])
                        flash("Class code succesfully updated")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_class_code(request.form["class_code"])[1]
    else:
        return redirect(url_for("login"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_class_code(), attribute="class_code", type = "text", error=error)

@app.route("/admin/create_user", methods=["GET","POST"])
def create_user():
    error = ""
    if user_required("admin") == True:
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
                if request.form["admin_passphrase"] == config.ADMIN_PASSPHRASE:
                    with sqlite3.connect(config.DB) as con:
                        c = con.cursor()
                        c.execute("INSERT INTO users VALUES(?, ?, ?, ?, 'NONE', 'NONE')",
                                  (request.form["ID"],
                                  crypter.encrypt(bytes(request.form["name"], "utf-8")),
                                  generate_password_hash(request.form["passphrase"]),
                                  request.form["account_type"],request.form["class_code"],))
                    flash("User successfully added")
                else:
                    error = "Incorrect passphrase "
    else:
        return redirect(url_for("login"))
    return render_template("admin_create_user.html", error=error)

@app.route("/admin/delete_user/<user_ID>", methods=["GET","POST"])
def delete_user(user_ID):
    error = None
    if user_required("admin") == True:
        user = User(user_ID)
        if request.method == "POST":
            if request.form["passphrase"] == config.ADMIN_PASSPHRASE:
                user.delete()
                flash("User successfully deleted")
            else:
                error = "Incorrect passphrase"
    else:
        return redirect(url_for("login"))
    return render_template("admin_delete_user.html", error=error, user_ID=user_ID)

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
    return render_template("input_requirements.html", grades=VALID_GRADES, letters=ALPHABET, numbers=NUMBERS, symbols=SYMBOLS)

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
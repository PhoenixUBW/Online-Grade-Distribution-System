# Importing all the Flask modules I will be using
from flask import Flask, session, flash, render_template, request, redirect, url_for
# Importing Werkzeug modules that come installed when installing Flask, I use them for the password hashing
from werkzeug.security import generate_password_hash, check_password_hash
# Importing cryptography library I used for encryption and decryption
from cryptography.fernet import Fernet
# Importing os libary module I used to check whether the databases exist or no
import os.path
# Importing sqlite3 which I used throughout my program to communicate with my database
import sqlite3
# Importing datetime library I used to give the dates that the students' grades where updated
from datetime import date
# Importing my database creation file
from database_initialisation import create_user_db, create_grades_db
# Importing the two config modes from my config file
from config import DevConfig, ProductionConfig

#wtforms, sqlalchemy, django, postgreSQL, bcrypt, password salting - tesco advice - talk about security flaws

#TO-DO - uses stacks to make forwards and back buttons, securely kept keys, teacher's comments?, attendance, behaviour, predicted grade, puts a delay between login/password enter inputs after getting it wrong x times

#after a error the create user stuff goes bold?
#fix css and looks for updated teacher
#potential bug if u remove all a students subjects


# Initiating imported config objects

app = Flask(__name__)

config = DevConfig() # Defining which config settings you want to use, Dev/production

app.secret_key = config.get_SECRET_KEY() # Session key

crypter = Fernet(config.get_EN_KEY()) # Encryption object

# Creating tuples of valid data used for validation

VALID_GRADES = ("","A*","A","B","C","D","E","F") 
SYMBOLS = ("`","!",'"',"'","$","%","^","&","*","(",")","-","_","+","=","[","]","{","}","|",";",":","@","~","#",",","<",">",".","?","/")
NUMBERS = ("0","1","2","3","4","5","6","7","8","9")
ALPHABET = (" ","a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
           "z","A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
AVAILABLE_SUBJECTS = ("maths","english","science","art","IT")

# Checks whether databases have been created and creates them

if os.path.exists(config.get_USER_DB()) == False: 
    create_user_db()
if os.path.exists(config.get_GRADES_DB()) == False:
    create_grades_db()

# Defining validation functions

def valid_ID(data): # Takes in the ID as an argument
    """Checks whether the inputted data is a valid ID
    
    Returns True or False and error"""
    error = None # Error starts empty
    if data == "": # If the input is empty
        error = "No ID inputted" # Error is set to the appropriate message
        return False, error # False is returned along with the error message
    for char in data: # Checks all characters in the input
        if char not in NUMBERS: # If any of the characters isn't a number
            error = "IDs must only contain numbers"
            return False, error
    return True, error # If nothing flags up True is returned along with the empty error

def valid_name(data):
    """Checks whether the inputted data is a valid name
    
    Returns True or False and error"""
    error =  None
    for char in data: # Checks all characters in the input
        if char not in ALPHABET:
            error = "Names must only contain letters"
            return False, error
    if len(data) < 2: # If the input isn't a greater length than 1 character
        error = "Names must be greater than 1 character"
        return False, error
    return True, error

def valid_passphrase(data):
    """Checks whether the inputted data is a valid passphrase
    
    Returns True or False and error"""
    error = None 
    alpha = False # Setting of the checks to false
    num = False
    sym = False
    length = False
    for char in data: # For the characters in the input there must be atleast one letter number and symbol
        if char in ALPHABET:
            alpha = True
        if char in NUMBERS:
            num = True
        if char in SYMBOLS:
            sym = True
    if len(data) > 11: # The input must be atleast 12 charcters
        length = True
    else:
        error = "Passphrase must be greater than 11 characters"
    if alpha == False:
        error = "Passphrase has no alphabetic letters"
    if num == False:
        error = "Passphrase has no numbers"
    if sym == False:
        error = "Passphrase has no symbols"
    if alpha == True and num == True and sym == True and length == True: # If all the checks are valid then it returns true along with the empty error
        return True, error
    else:
        return False, error

def valid_account_type(data):
    """Checks whether the inputted data is a valid account type
    
    Returns True or False and error"""
    error = None
    if data != "Student" and data != "Teacher": # If the input isn't either Student or Teacher
        error = "Account type must = 'Student' or 'Teacher'"
        return False, error
    return True, error

def valid_class_code(data):
    """Checks whether the inputted data is a valid class code
    
    Returns True or False and error"""
    error = None
    if data == "":
        error = "No class code inputted "
        return False, error
    for char in data: # For every character in the input
        if char not in ALPHABET and char not in NUMBERS: # It is false if that character isn't a letter or a number
            error = "Class code must only contain alphabetic and numeric characters"
            return False, error
    return True, error

def valid_grade(data):
    """Checks whether the inputted data is a valid grade
    
    Returns True or False and error"""
    error = None
    if data not in VALID_GRADES: # Not valid unless grade is from set of valid grades
        error = "Grade must be in our set of valid grades"
        return False, error
    return True, error

def list_ID():
    """Creates a list of all users' IDs in the database"""
    with sqlite3.connect(config.get_USER_DB()) as con: # Connects to the user database
        c = con.cursor()
        c.execute("SELECT ID FROM users") # Selects all the IDs
        temp = c.fetchall() # Returns a list containing tuples
    IDs = list() 
    for ID in temp: # Iterates through the list of tuples
        IDs.append(str(ID[0])) # Converts the first item in each tuple to a string and adds them to the list ID which creates the list of str IDs
    return IDs

def user_required(ID):
    """Checks whether the user is firstly logged in then whether the current user's ID matches the required ID passed in"""
    if "ID" in session: # If ID is in the session dictionary (someone has logged in)
        if session["ID"] == ID: # And if the ID saved in the session matches the required ID
            return True # True is returned
        else: # Else error message is flashed, flash is a flask function which can be used to dynamically display messages on the website
            flash("You are not logged in as the required user to view this page")
            return False
    else:
        flash("You must be logged in to view this page")
        return False
    
def logged_in():
    """Determines if the user is logged in and then returns a string saying who they are logged in as
    
    used to display the login status on html"""
    if "ID" in session: # If someone is logged in
        if session["ID"] == "admin": # As admin is hardcoded it is dealt with differently 
            return "Logged in as: Admin"
        else:
            user=User(session["ID"]) # Creates a user object with the current ID 
            return f"Logged in as: {user.get_name()}" # Retrieves and displays their name
    else:
        return "Login"

class Student():
    """Provides student information to the User class with composition"""
    def __init__(self,ID): # Takes in ID as a parameter
        with sqlite3.connect(config.get_GRADES_DB()) as con: # Connects to the student database
            c = con.cursor()
            c.execute("SELECT subject ,grade, date_updated FROM grades WHERE ID=?",(ID,)) # Selects subjects, grades, and dates where the ID is the ID for the student the object has been modelled on
            subjects = []
            grades = []
            dates = []
            fetch = c.fetchall() # Returns a list containing tuples
            for row in fetch: # Goes through the list take the data from the tuples and appending them to the lists for the student
                subjects.append(row[0])
                grades.append(crypter.decrypt(row[1]).decode("UTF-8")) # Some data must be decrypted when retrieved
                dates.append(crypter.decrypt(row[2]).decode("UTF-8"))
        num_subjects = []
        for x in range(0,len(subjects)):
            num_subjects.append(x)
        self.__subjects = subjects # Data is then set as an object private attribute
        self.__grades = grades
        self.__dates = dates
        self.__num_subjects = num_subjects # Used to display subjects in html

    def get_subjects(self): # Data is accessed with get methods
        return self.__subjects

    def get_grades(self):
        return self.__grades

    def get_dates(self):
        return self.__dates
    
    def get_num_subjects(self):
        return self.__num_subjects

class Teacher():
    """Provides admin functionality to the User class with composition"""
    def __init__(self,target): # Target ID is passed in as a parameter
        self.__target = target # Target set as a private attriute to be used within the class

    def update_grade(self,newgrade,subject):
        """Replaces the target's grade with the new grade"""
        with sqlite3.connect(config.get_GRADES_DB()) as con: # Connects to the student grade database
            c = con.cursor()
            c.execute("UPDATE grades SET grade=?, date_updated=? WHERE ID=? AND subject=?",(crypter.encrypt(bytes(newgrade, "utf-8")), crypter.encrypt(bytes(str(date.today()), "utf-8")), self.__target, subject)) # Updates the grade with the new encrypted grade and encryted today's date for target ID and specified subject
    
    def add_subjects(self,subject):
        """Gives the target more subjects"""
        with sqlite3.connect(config.get_GRADES_DB()) as con:
            c = con.cursor()
            c.execute("DELETE FROM grades WHERE ID=? AND subject='NONE'",(self.__target,)) # Before adding the subject, if the student previously had no subjects the NONE is removed
            c.execute("INSERT INTO grades VALUES(?,?,?,?)",(self.__target,subject,crypter.encrypt(bytes("NONE", "utf-8")),crypter.encrypt(bytes("NONE", "utf-8"))))
    
    def remove_subjects(self,subject):
        """Removes subjects from the target"""
        with sqlite3.connect(config.get_GRADES_DB()) as con:
            c = con.cursor()
            c.execute("DELETE FROM grades WHERE ID=? AND subject=?",(self.__target,subject))

class Admin():
    """Provides admin functionality to the User class with composition"""
    def __init__(self,target): # Takes in the target ID and sets it as a priv attribute as with the Teacher class
        self.__target = target

    def update_name(self,newname):
        """Replaces the target's name with the new name"""
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET name=? WHERE ID=?",(crypter.encrypt(bytes(newname, "utf-8")), self.__target))

    def update_passphrase(self, newpassphrase):
        """Replaces the target's passphrase with the new passphrase"""
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET hashed_passphrase=? WHERE ID=?",(generate_password_hash(newpassphrase), self.__target))

    def update_class_code(self, newclass_code):
        """Replaces the target's class code with the new class code"""
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("UPDATE users SET class_code=? WHERE ID=?",(newclass_code, self.__target))

    def delete(self):
        """Deletes the target from the database"""
        with sqlite3.connect(config.get_USER_DB()) as con: # Data for the target ID is deleted from both databases
            c = con.cursor()
            c.execute("DELETE FROM users WHERE ID=?",(self.__target,))
        with sqlite3.connect(config.get_GRADES_DB()) as con:
            c = con.cursor()
            c.execute("DELETE FROM grades WHERE ID=?",(self.__target,))

class User():
    """Models a user in the database to hold their information and perform actions on them"""
    def __init__(self,ID):
        with sqlite3.connect(config.get_USER_DB()) as con: # Connects to the user database
            c = con.cursor()
            c.execute("SELECT * FROM users WHERE ID=?",(ID,)) # Selects all info for target ID
            info = c.fetchall()[0]
        self.__ID = info[0] # Creates attributes containing all the user's user information
        self.__name = crypter.decrypt(info[1]).decode("UTF-8")
        self.__hashed_passphrase = info[2]
        self.__passphrase = "unavailable"
        self.__account_type = info[3]
        self.__class_code = info[4]
        if "ID" in session: # If someone is logged in
            if self.__account_type == "Student": # Depending on their account type they will have access to data/functions from other classes
                self.student = Student(ID) # Uses composition to use functionality from other classes
            if "account_type" in session:
                if session["account_type"] == "Teacher":
                    self.teacher = Teacher(ID)
            if session["ID"] == config.get_ADMIN_USERNAME():
                self.admin = Admin(ID)

    def get_ID(self): # Information is retrieved in main using get methods
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
    
@app.errorhandler(404) # Displays the 404 error page if a 404 is returned
def not_found(error_number):
    return render_template("404.html", logged_in=logged_in()) # Returns the 404 template and the result of the logged_in function to display who is currently logged in

@app.route("/") # When a user accesses domain.name/ it will display the homepage template
def homepage():
    error = None
    return render_template("homepage.html", error=error, logged_in=logged_in())

@app.route("/login", methods=["GET","POST"]) # Uses the GET and POST http methods
def login():
    error = None
    if request.method == "POST": # If using the request method POST
        if request.form["ID"] == config.get_ADMIN_USERNAME() and request.form["passphrase"] == config.get_ADMIN_PASSPHRASE():
            session["ID"] = config.get_ADMIN_USERNAME()
            return redirect(url_for("admin_homepage")) # if the form ID and passphrase matches the admin login then it will redirect them to the admin homepage
        IDs = list_ID() # Creates a list of all IDs
        if valid_ID(request.form["ID"])[0] == True and request.form["ID"] in IDs: # Checks the ID is valid and an ID in the database
            user = User(request.form["ID"]) # Once ID is validated a user object is created with that ID
            if valid_passphrase(request.form["passphrase"])[0] == True and check_password_hash(user.get_hashed_passphrase(),request.form["passphrase"]) == True: # Checks that the passphrase for the entered ID is the same as the entered passphrase
                session["ID"] = str(user.get_ID()) # Sets the session ID and session account type to equal the ID and account type of the user object
                session["account_type"] = user.get_account_type() 
                flash("You have succesfully been logged in")                
                if user.get_account_type() == "Student": # Redirects you to the appropriate page depending on your account type and ID
                    return redirect(f"/student/{user.get_ID()}")
                elif user.get_account_type() == "Teacher":
                    return redirect(f"/teacher/{user.get_ID()}")
            else:
                error = "Invalid passphrase"
        else:
            error = "Invalid ID"
    return render_template("login.html", error=error, logged_in=logged_in())

@app.route("/student/<student_ID>") # Student homepage, displays the student's info
def student_homepage(student_ID):
    error = None
    if user_required(student_ID) == True: # Checks that the currently logged in used can access this page
        student = User(student_ID) # If check is fine then it creates the student object
    else:
        return redirect(url_for("login"))
    return render_template("student_homepage.html", student=student, error=error, logged_in=logged_in()) # The student object is passed into the template where the attributes can be accessed

@app.route("/teacher/<teacher_ID>") # Teacher homepage, displays students in teachers class
def teacher_homepage(teacher_ID):
    error = None
    if user_required(teacher_ID) == True: # Validates user
        teacher = User(teacher_ID)
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type=? AND class_code=?",("Student",teacher.get_class_code())) # Retrieves all the students in the teachers class
            lt_students = c.fetchall() 
            students = list()
            for student in lt_students: # Creates a list of student objects 
                students.append(User(student[0]))
    else:
        return redirect(url_for("login"))

    return render_template("teacher_homepage.html",students=students, teacher=teacher, error=error, logged_in=logged_in())

@app.route("/teacher/<teacher_ID>/view_student/<student_ID>") # Viewing selected student page, displays selected student info
def teacher_view_student(teacher_ID,student_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        student = User(student_ID)
        if teacher.get_class_code() != student.get_class_code(): # Validates that the student being viewed is in the class of the currently logged in teacher
            error = "This student is not in your class"
    return render_template("teacher_view_student.html", student=student, teacher=teacher, error=error, logged_in=logged_in())

@app.route("/teacher/<teacher_ID>/add_subjects/<student_ID>", methods=['GET', 'POST']) # Adding subjects page, displays current subjects and subjects you could add
def teacher_add_subjects(teacher_ID,student_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        student = User(student_ID)
        if teacher.get_class_code() == student.get_class_code():
            if request.method == "POST":
                if check_password_hash(teacher.get_hashed_passphrase(), request.form["passphrase"]) == True: # Teacher password confirmation
                    for subject in AVAILABLE_SUBJECTS: # Goes through all the available subjects checking whether they have been asked to be added
                        if subject not in student.student.get_subjects():
                            if subject in request.form:
                                if request.form[subject] == "True":
                                    student.teacher.add_subjects(subject) # Uses the student object with the composite teacher object to call the add subjects method
                    flash("Subject successfully added, resfresh to see changes")
                else:
                    error = "Incorrect password"
        else:
            error = "This student is not in your class"
    else:
        return redirect(url_for("login"))
    return render_template("teacher_add_subjects.html", student=student, teacher=teacher, error=error, logged_in=logged_in())

@app.route("/teacher/<teacher_ID>/remove_subjects/<student_ID>", methods=['GET', 'POST']) # Removing subjects page, displays current subjects and subjects you could remove
def teacher_remove_subjects(teacher_ID,student_ID):
    error = None
    if user_required(teacher_ID) == True:
        teacher = User(teacher_ID)
        student = User(student_ID)
        if teacher.get_class_code() == student.get_class_code():
            if request.method == "POST":
                if check_password_hash(teacher.get_hashed_passphrase(), request.form["passphrase"]) == True:
                    for subject in AVAILABLE_SUBJECTS:
                        if subject in student.student.get_subjects():
                            if subject in request.form:
                                if request.form[subject] == "True":
                                    student.teacher.remove_subjects(subject)
                    flash("Subject successfully removed, resfresh to see changes")
                else:
                    error = "Incorrect password"
        else:
            error = "This student is not in your class"
    else:
        return redirect(url_for("login"))
    return render_template("teacher_remove_subjects.html", student=student, teacher=teacher, error=error, logged_in=logged_in())

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
                        student.teacher.update_grade(request.form["grade"],student.student.get_subjects()[int(subject_index)])
                        flash("Grade successfully updated, refresh to see changes")
                    else:
                        error = "Incorrect password "
                else:
                    error = valid_grade(request.form["grade"])[1]
        else:
            error = "This student is not in your class "
    else:
        return redirect(url_for("login"))
    return render_template("teacher_update_grade.html", student=student, teacher=teacher, error=error, logged_in=logged_in(), subject_index=int(subject_index))

@app.route("/admin") # Admin homepage, displays a list of users
def admin_homepage():
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True: # Takes the admin username from config object
        with sqlite3.connect(config.get_USER_DB()) as con:
            c = con.cursor()
            c.execute("SELECT ID FROM users WHERE account_type='Student' OR account_type='Teacher'")
            lt_users = c.fetchall()
            users = list()
            for user in lt_users:
                users.append(User(user[0])) # Adds a series of user objects to a list
    else:
        return redirect(url_for("login"))
    return render_template("admin_homepage.html", users=users, error=error, logged_in=logged_in())

@app.route("/admin/update_name/<user_ID>", methods=["GET","POST"]) # Admin update name page
def update_name(user_ID):
    error = None
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_name(request.form["attribute"])[0] == True: # Validates the attributes
                if request.form["attribute"] == request.form["confirm_attribute"]: # Confirms the attribute matches the second entry
                    if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE(): # Confirms the admin passphrase
                        user.admin.update_name(request.form["attribute"]) # Updates the attribute
                        flash("Name succesfully updated, refresh to see changes!")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_name(request.form["attribute"])[1]
    else:
        return redirect(url_for("admin"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_name(), attribute="Name", type = "text", error=error, logged_in=logged_in()) # Passing in these extra variables value, attribute, and text reduce what would be 3 html files to 1

@app.route("/admin/update_passphrase/<user_ID>", methods=["GET","POST"]) # Admin update passphrase page
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

@app.route("/admin/update_class_code/<user_ID>", methods=["GET","POST"]) # Admin update class code page
def update_class_code(user_ID):
    error = ""
    if user_required(config.get_ADMIN_USERNAME()) == True:
        user = User(user_ID)
        if request.method == "POST":
            if valid_class_code(request.form["attribute"])[0] == True:
                if request.form["attribute"] == request.form["confirm_attribute"]:
                    if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                        user.admin.update_class_code(request.form["attribute"])
                        flash("Class code succesfully updated, refresh to see changes!")
                    else:
                        error = "Incorrect passphrase "
                else:
                    error = "Please ensure both fields contain the same information "
            else:
                error = valid_class_code(request.form["attribute"])[1]
    else:
        return redirect(url_for("login"))
    return render_template("admin_edit_attribute.html", user=user, value=user.get_class_code(), attribute="Class Code", type = "text", error=error, logged_in=logged_in())

@app.route("/admin/create_user", methods=["GET","POST"]) #Create user page, asks for inputs for every field needed to create a new user
def create_user():
    error = ""
    if user_required(config.get_ADMIN_USERNAME()) == True:
        valid_user = True
        if request.method == "POST":
            IDs = list_ID()
            if request.form["ID"] in IDs: # Checks whether the ID is already in use
                valid_user = False
                error = "There is already an existing user with this ID "
            if valid_ID(request.form["ID"])[0] == False: # Validates all the entries
                valid_user = False
                error = valid_ID(request.form["ID"])[1]
            if valid_name(request.form["name"])[0] == False:
                valid_user = False
                error + valid_name(request.form["name"])[1]
            if valid_passphrase(request.form["passphrase"])[0] == False:
                valid_user = False
                error = valid_passphrase(request.form["passphrase"])[1]
            if "account_type" in request.form:
                if valid_account_type(request.form["account_type"])[0] == False:
                    valid_user = False
                    error = valid_account_type(request.form["account_type"])[1]
            else:
                valid_user = False
                error = "Select an account type"
            if valid_class_code(request.form["class_code"])[0] == False:
                valid_user = False
                error = valid_class_code(request.form["class_code"])[1]
            if valid_user == True:
                if request.form["admin_passphrase"] == config.get_ADMIN_PASSPHRASE():
                    with sqlite3.connect(config.get_USER_DB()) as con:
                        c = con.cursor()
                        c.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?)", # Adds user to the database
                                  (request.form["ID"],
                                  crypter.encrypt(bytes(request.form["name"], "utf-8")),
                                  generate_password_hash(request.form["passphrase"]),
                                  request.form["account_type"],
                                  request.form["class_code"]))
                    if request.form["account_type"] == "Student": # If it's a student the necessary info is also added to the grades database
                        with sqlite3.connect(config.get_GRADES_DB()) as con:
                            c = con.cursor()
                            c.execute("INSERT INTO grades VALUES(?,'NONE',?,?)",(request.form["ID"],crypter.encrypt(bytes("NONE", "utf-8")),crypter.encrypt(bytes("NONE", "utf-8"))))
                    flash("User successfully added")
                else:
                    error = "Incorrect passphrase "
    else:
        return redirect(url_for("login"))
    return render_template("admin_create_user.html", error=error, logged_in=logged_in())

@app.route("/admin/delete_user/<user_ID>", methods=["GET","POST"]) # Delete user page
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

@app.route("/logout") # Logout function
def logout():
    if "ID" in session:
        session.pop("ID",None) # Removes ID from the session and replaces it with nothing
        flash("You have been logged out")
    else:
        flash("You are not logged in")
    return redirect(url_for("login"))

@app.route("/current_user/<previous_url>") # Current user functionality
def current_user(previous_url):
    if "ID" in session:
        flash(f"ID: {session['ID']} is logged in")
    else:
        flash("No user is logged in")
    return redirect(url_for(previous_url))

@app.route("/input_requirements") # Input requirement page
def input_requirements():
    return render_template("input_requirements.html", grades=VALID_GRADES, letters=ALPHABET, numbers=NUMBERS, symbols=SYMBOLS, logged_in=logged_in())

if __name__ == "__main__":
    app.run(debug=config.get_DEBUG())
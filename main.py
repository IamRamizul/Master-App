from flask import Flask, render_template, request, url_for, redirect, flash
from werkzeug.routing import BaseConverter

# from werkzeug.security import generate_password_hash, check_password_hash
import pymongo



class BoolConverter(BaseConverter):
    regex = '(True|False)'

    def to_python(self, value):
        return value.lower() == 'true'

    def to_url(self, value):
        return str(value).lower()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_key'
app.config['TESTING'] = False
app.url_map.converters['bool'] = BoolConverter



client = pymongo.MongoClient("mongodb+srv://Ramiz-admin:kxhAAKBDbRyZYm5l@cluster0.sub9uhj.mongodb.net/?retryWrites=true&w=majority")
db = client["MasterClasses"]
staff = db["staff"]





@app.route("/")
def home():
  
    return render_template("Home.html")

@app.route("/login",methods = ["GET", "POST"])
def login():
    
    status = "login"
    if request.method  == "POST" : 
        email = request.form.get("email")
        password = request.form.get("password")
        user = staff.find_one({"email" : email, "password" : password})

        if not (user and password == user["password"]):
            flash("The email and password entered don't match, please try again.")
        else:
            userEmail = user["email"]
            if userEmail == "masterclassesrashid@gmail.com":
                return redirect(url_for("staffs"))
            return redirect(f'/tasks/{userEmail}/{False}')
    

    return render_template("Login.html", status = status)

@app.route("/signin", methods = ["GET", "POST"])
def signin():
    status = "signin"
    staff = db["staff"]

    if request.method  == "POST" : 
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_data = staff.find_one({'email': email})

        if user_data:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))

        new_staff = {
            "name" : name,
            "email" : email,
            "password" : password,
            "tasks" : []
        }
        staff.insert_one(new_staff) 

        return redirect(url_for('login'))

    return render_template("login.html", status = status)


@app.route("/tasks/<email>/<bool:admin>", methods = ["GET", "POST"])
def tasks(email, admin): 
    staffName = staff.find_one({"email" : email})

    if request.method == "POST":
        new_task = request.form.get("task")

        new_task_dict = {
        "taskName" : new_task, 
        "is_completed" : "",
        "is_verified" : ""
        }
        # print(staffName)
        staffName["tasks"].append(new_task_dict)
        staff.update_one({"email": email},{"$set" : staffName})

        return render_template("Tasks.html", email = email, staffName = staffName, tasks = staffName['tasks'], admin = admin) # )
    
    # print(staffName)
    return render_template("Tasks.html", email = email, staffName = staffName, tasks = staffName['tasks'], admin = admin)
    # return render_template("Tasks.html", email = email, staffName = staffName,tasks = staffName['tasks'])

@app.route("/logout")
def logout():
    return redirect(url_for('home'))

@app.route("/staff")
def staffs():
    staff = db["staff"]
    
    cursor = staff.find()

    

    return render_template("staff.html", documents = cursor )

@app.route("/deleteTask/<int:index>/<email>", methods = ["POST"])
def delete_task(index, email):
    staffName = staff.find_one({"email" : email})

    # staffName["tasks"].pop(index)
    del staffName["tasks"][index]
    staff.update_one({"email": email},{"$set" : staffName})

    return render_template("Tasks.html", email = email, staffName = staffName, tasks = staffName['tasks'], admin = True)


@app.route("/check/<int:index>/<email>", methods = ["POST"])
def check(index, email):
    staffName = staff.find_one({"email" : email})
    is_completed = staffName["tasks"][index]["is_completed"]
    if is_completed == "":
        staffName["tasks"][index]["is_completed"] = True
        print(True)
    elif is_completed == True:
        staffName["tasks"][index]["is_completed"] = False
        print(False)
    else :
        staffName["tasks"][index]["is_completed"] = True
        print(True)
    
    staff.update_one({"email": email},{"$set" : staffName})

    return render_template("Tasks.html", email = email, staffName = staffName, tasks = staffName['tasks'])

@app.route("/verify/<int:index>/<email>", methods = ["POST"])
def verify(index, email):
    staffName = staff.find_one({"email" : email})
    is_verified = staffName["tasks"][index]["is_verified"]
    if is_verified == "":
        staffName["tasks"][index]["is_verified"] = True
        print(True)
    elif is_verified == True:
        staffName["tasks"][index]["is_verified"] = False
        print(False)
    else :
        staffName["tasks"][index]["is_verified"] = True
        print(True)
    
    staff.update_one({"email": email},{"$set" : staffName})

    return render_template("Tasks.html", email = email, staffName = staffName, tasks = staffName['tasks'] , admin = True)

        



if __name__ == '__main__':
    app.run(debug=True)
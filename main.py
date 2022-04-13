from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import sqlite3
from datetime import datetime

con = sqlite3.connect('HarmanStories.db', check_same_thread=False)

cursor = con.cursor()

user_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='USERS'").fetchall()

if user_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE USERS(
                            ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME TEXT,
                            EMAIL TEXT,
                            USERNAME TEXT,
                            PASSWORD TEXT,
                            DATE_CREATED TEXT); ''')
    print("Table has created")

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        getEmail = request.form["email"]
        getPswd = request.form["pswd"]
        # print(getEmail)
        # print(getPswd)
        try:
            query = "SELECT * FROM USERS WHERE EMAIL = '" + getEmail + "' AND PASSWORD = '" + getPswd + "'"
            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
            if len(result) == 0:
                print("Invalid User")
                flash("Invalid User")
            else:
                for i in result:
                    getName = i[1]
                    getid = i[0]

                    session["name"] = getName
                    session["id"] = getid
                    print("success")
                return redirect("/home")
        except Exception as e:
            print(e)
    return render_template("login.html")


@app.route("/register-user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        getname = request.form["name"]
        getEmail = request.form["email"]
        getUsername = request.form["username"]
        getPswd = request.form["pswd"]
        curr_date = datetime.now().date()

        print(getname)
        print(getEmail)
        print(getUsername)
        print(getPswd)
        print(curr_date)

        try:
            data = (getname, getEmail, getUsername, getPswd, curr_date)
            insert_query = '''INSERT INTO USERS(NAME, EMAIL, USERNAME, PASSWORD, DATE_CREATED) 
                                VALUES (?,?,?,?,?)'''

            cursor.execute(insert_query, data)
            con.commit()
            print("User Registered successfully")
            return redirect("/")

        except Exception as e:
            print(e)
    return render_template("signup.html")


@app.route("/home", methods=["GET", "POST"])
def Home():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        try:
            return render_template("user_home.html")
        except Exception as e:
            print(e)
        return render_template("user_home.html")


if __name__ == "__main__":
    app.run()

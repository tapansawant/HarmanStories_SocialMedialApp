from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
import sqlite3
from datetime import datetime

con = sqlite3.connect('socialmedia.db', check_same_thread=False)

cursor = con.cursor()

user_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='USERS'").fetchall()
post_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='POSTS'").fetchall()

if user_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE USERS(
                            USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME TEXT,
                            EMAIL TEXT,
                            USERNAME TEXT,
                            PASSWORD TEXT,
                            DATE_CREATED TEXT); ''')
    print("Table has created")

if post_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE POSTS(
                            POST_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            TEXT_BOX TEXT,
                            P_USERNAME TEXT,
                            P_DATE_CREATED TEXT,
                            FOREIGN KEY (P_USERNAME)
                                REFERENCES USERS(USER_ID)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE); ''')
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
        try:
            query = "SELECT * FROM USERS WHERE EMAIL = '" + getEmail + "' AND PASSWORD = '" + getPswd + "'"
            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
            if len(result) == 0:
                print("Invalid User")
                flash("Invalid User", category='error')
            else:
                for i in result:
                    getName = i[3]
                    getid = i[0]
                    session["name"] = getName
                    session["id"] = getid
                    flash("Logged in!", category='success')
                    # login_user(user, remember=True)
                    print("success")
                return redirect("/home")
        except Exception as e:
            print(e)
    return render_template("login.html")


@app.route("/sign-up", methods=["GET", "POST"])
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
            flash('User created!')
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
            logged_in = True
            cursor.execute("SELECT * FROM POSTS")
            posts = cursor.fetchall()
            print(posts)
            return render_template("home.html", posts=posts, user_is_authenticated=logged_in)
        except Exception as e:
            print(e)
    # return render_template("home.html", user_is_authenticated=True)


@app.route("/create-post", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        text = request.form["text"]
        curr_date = datetime.now().date()
        userName = session["name"]

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            data = (text, userName, curr_date)
            insert_query = '''INSERT INTO POSTS(TEXT_BOX,P_USERNAME,P_DATE_CREATED) 
                                            VALUES (?,?,?)'''
            cursor.execute(insert_query, data)
            con.commit()
            flash('Post created!', category='success')
            return redirect("#")

    return render_template('create_post.html')


if __name__ == "__main__":
    app.run()

from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_session import Session
import sqlite3
from datetime import datetime
from flask_socketio import SocketIO

con = sqlite3.connect('Harmanstories11.db', check_same_thread=False)

cursor = con.cursor()

user_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='USERS'").fetchall()
post_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='POSTS'").fetchall()
comment_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='POSTS'").fetchall()
like_table = con.execute("SELECT name from sqlite_master WHERE type='table' AND name='POSTS'").fetchall()

if user_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE USERS(
                            USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            NAME TEXT,
                            EMAIL TEXT,
                            USERNAME TEXT,
                            PASSWORD TEXT,
                            DATE_CREATED TEXT,
                            DOB TEXT,
                            IMAGELINK TEXT); ''')
    print("Table has created")

if post_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE POSTS(
                            POST_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            TEXT_BOX TEXT,
                            P_USERNAME TEXT,
                            P_DATE_CREATED TEXT,
                            LIKE INTEGER DEFAULT 0 NOT NULL,
                            IMAGELINK TEXT,
                            FOREIGN KEY (P_USERNAME)
                                REFERENCES USERS(USERNAME)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE); ''')
    print("Table has created")

if comment_table:
    print("Table Already Exists ! ")
else:
    con.execute(''' CREATE TABLE COMMENTS(
                            COMMENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            P_ID INTEGER,
                            COMMENT_TEXT_BOX TEXT,
                            C_USERNAME TEXT,
                            C_DATE_CREATED TEXT,
                            FOREIGN KEY (P_ID)
                                REFERENCES POSTS(POST_ID)
                                ON UPDATE CASCADE
                                ON DELETE CASCADE); ''')
    print("Table has created")

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
Session(app)
socketio = SocketIO(app)


@app.route("/chat")
def sessions():
    return render_template('session.html', user_is_authenticated=True)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


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
                    getImage = i[7]
                    session["name"] = getName
                    session["id"] = getid
                    session["dp"] = getImage
                    flash("Logged in!", category='success')
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
        curr_date = datetime.now()

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
            # cursor.execute("SELECT * FROM POSTS ")
            cursor.execute('''SELECT POSTS.POST_ID,POSTS.TEXT_BOX,POSTS.P_USERNAME,POSTS.P_DATE_CREATED,POSTS.LIKE,POSTS.IMAGELINK,
                                USERS.IMAGELINK     
                                FROM USERS
                                INNER JOIN POSTS
                                ON POSTS.P_USERNAME = USERS.USERNAME''')
            posts = cursor.fetchall()
            print(posts)
            return render_template("home.html", posts=posts, user_is_authenticated=logged_in, username=session['name'])
        except Exception as e:
            print(e)
    # return render_template("home.html", user_is_authenticated=True)


@app.route("/create-post", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        text = request.form["text"]
        curr_date = datetime.now()
        userName = session["name"]
        destination_path = ""
        fileobj = request.files['file']
        file_extensions = ["JPG", "JPEG", "PNG", "GIF"]
        uploaded_file_extension = fileobj.filename.split(".")[1]
        if uploaded_file_extension.upper() in file_extensions:
            destination_path = f"static/uploads/{fileobj.filename}"
            fileobj.save(destination_path)
            data = (text, userName, curr_date, destination_path)
            insert_query = '''INSERT INTO POSTS(TEXT_BOX,P_USERNAME,P_DATE_CREATED,IMAGELINK) 
                                                        VALUES (?,?,?,?)'''
            cursor.execute(insert_query, data)
            con.commit()
            flash('Post created!', category='success')
            return redirect("/home")
        else:
            flash("only images are accepted")
            return render_template('home2.html')
    return render_template('create_post.html', user_is_authenticated=True)


@app.route("/my-profile", methods=["GET", "POST"])
def profile():
    if not session.get("name"):
        return redirect("/")
    else:
        getUserName = session["name"]
        print(getUserName)
        try:
            cursor.execute("SELECT* FROM USERS WHERE USERNAME= '" + getUserName + "'")
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            if len(result) == 0:
                print("Invalid Data")
            else:
                print(result)
                return render_template("profile2.html", user=result, user_is_authenticated=True)
        except Exception as e:
            print(e)
        return render_template("/profile.html", user_is_authenticated=True)


@app.route("/update-profile", methods=["GET", "POST"])
def update_profile():
    if not session.get("name"):
        return redirect("/")
    else:
        getUserName = session["name"]
        print(getUserName)
        try:
            if request.method == "POST":
                getName = request.form["Name"]
                getUsername = request.form["username"]
                getEmail = request.form["email"]
                getdob = request.form["dob"]
                destination_path = ""
                fileobj = request.files['file']
                file_extensions = ["JPG", "JPEG", "PNG", "GIF"]
                uploaded_file_extension = fileobj.filename.split(".")[1]
                if uploaded_file_extension.upper() in file_extensions:
                    destination_path = f"static/uploads/{fileobj.filename}"
                    fileobj.save(destination_path)
                    data = (getName, getEmail, getUsername, getdob, destination_path, getUserName)
                    insert_query = '''UPDATE USERS SET NAME = ?,EMAIL=?,USERNAME=?,DOB=?,IMAGELINK=?
                                       where USERNAME = ?'''

                    cursor.execute(insert_query, data)
                    print("SUCCESSFULLY UPDATED!")
                    con.commit()
                    return redirect("/my-profile")
                else:
                    flash("only images are accepted")
                    return render_template('profile2.html')

        except Exception as e:
            print(e)


@app.route("/profile-username", methods=["GET", "POST"])
def userprofile():
    if not session.get("name"):
        return redirect("/")
    else:
        getUserName = request.args.get('username')
        print(getUserName)
        try:
            cursor.execute("SELECT* FROM USERS WHERE USERNAME= '" + getUserName + "'")
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            if len(result) == 0:
                print("Invalid Data")
            else:
                print(result)
                return render_template("profilebyusername.html", user=result, user_is_authenticated=True)
        except Exception as e:
            print(e)
        return render_template("/profilebyusername.html", user_is_authenticated=True)


@app.route("/my-posts", methods=["GET", "POST"])
def posts():
    if not session.get("name"):
        return redirect("/")
    else:
        getUserName = session["name"]
        print(getUserName)
        try:
            cursor.execute("SELECT * FROM POSTS WHERE P_USERNAME= '" + getUserName + "'")
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            if len(result) == 0:
                print("Invalid Data")
                flash('No posts yet...!', category='error')
                return redirect("/home")
            else:
                print(result)
                return render_template("mypost.html", posts=result, user_is_authenticated=True, username=session["name"])
        except Exception as e:
            print(e)


@app.route("/logout", methods=["GET", "POST"])
def userlogout():
    if not session.get("name"):
        return redirect("/")
    else:
        session["name"] = None
        return redirect("/")


@app.route("/view-comments", methods=["GET", "POST"])
def ViewComments():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        try:
            getId = request.args.get('id')
            Q = '''SELECT POSTS.POST_ID,POSTS.TEXT_BOX,POSTS.P_USERNAME,POSTS.P_DATE_CREATED,
                    COMMENTS.COMMENT_ID,COMMENTS.P_ID,COMMENTS.COMMENT_TEXT_BOX,COMMENTS.C_USERNAME,COMMENTS.C_DATE_CREATED,
                    POSTS.IMAGELINK
                    FROM POSTS
                    INNER JOIN COMMENTS
                    ON POSTS.POST_ID = COMMENTS.P_ID
                    WHERE POST_ID = ?'''
            cursor.execute(Q, (getId,))
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            print(result)
            return render_template("view-comments.html", posts=result, user_is_authenticated=True,
                                   username=session['name'])
        except Exception as e:
            print(e)


@app.route("/create-comment", methods=["GET", "POST"])
def create_comment():
    getId = request.args.get('id')
    if request.method == "POST":
        text = request.form["text"]
        curr_date = datetime.now().date()
        userName = session["name"]

        if not text:
            flash('Comment cannot be empty', category='error')
        else:
            data = (text, getId, userName, curr_date)
            insert_query = '''INSERT INTO COMMENTS(COMMENT_TEXT_BOX,P_ID,C_USERNAME,C_DATE_CREATED) 
                                            VALUES (?,?,?,?)'''
            cursor.execute(insert_query, data)
            con.commit()
            flash('Commented.....!', category='success')
            return redirect("/home")
    return render_template('create-comment.html', user_is_authenticated=True)


@app.route("/edit-post", methods=["GET", "POST"])
def edit_post():
    getId = request.args.get('id')
    try:
        if request.method == "POST":
            text = request.form["text"]
            destination_path = ""
            fileobj = request.files['file']
            file_extensions = ["JPG", "JPEG", "PNG", "GIF"]
            uploaded_file_extension = fileobj.filename.split(".")[1]
            if uploaded_file_extension.upper() in file_extensions:
                destination_path = f"static/uploads/{fileobj.filename}"
                fileobj.save(destination_path)
                data = (text, destination_path, getId)
                update_query = "UPDATE POSTS SET TEXT_BOX=?,IMAGELINK=? WHERE POST_ID = ?"
                cursor.execute(update_query, data)
                print("updated successfully")
                con.commit()
                flash('Post edited!', category='success')
                return redirect("/home")
            else:
                flash("only images are accepted")
                return render_template('home.html')
    except Exception as e:
        print(e)
    return render_template('edit-post.html', user_is_authenticated=True)


@app.route("/delete-post", methods=["GET", "POST"])
def delete_post():
    getId = request.args.get('id')
    try:
        Q = "DELETE FROM POSTS WHERE POST_ID = ?"
        cursor.execute(Q, (getId,))
        print("SUCCESSFULLY DELETED!")
        con.commit()
        return redirect("/home")
    except Exception as e:
        print(e)


@app.route("/delete-comment", methods=["GET", "POST"])
def delete_comment():
    getId = request.args.get('id')
    try:
        Q = "DELETE FROM COMMENTS WHERE COMMENT_ID = ?"
        cursor.execute(Q, (getId,))
        print("SUCCESSFULLY DELETED!")
        con.commit()
        return redirect("/home")
    except Exception as e:
        print(e)


@app.route("/like", methods=["GET", "POST"])
def like():
    getId = request.args.get('id')
    q = "SELECT LIKE FROM POSTS WHERE POST_ID = ?"
    cursor.execute(q, (getId,))
    print("SUCCESSFULLY SELECTED!")
    count = cursor.fetchall()
    print(count)
    like_count = 0
    for i in count:
        like_count = i[0]
    like_count = like_count + 1

    try:
        data = (like_count, getId)
        Q = "UPDATE POSTS SET LIKE = ? where POST_ID=? "
        cursor.execute(Q, data)
        print("SUCCESSFULLY updated!")
        con.commit()
        return redirect("/home")
    except Exception as e:
        print(e)


@app.route("/view-all-users", methods=["GET", "POST"])
def Viewusers():
    if not session.get("name"):
        return redirect("/login-user")
    else:
        try:
            cursor.execute("SELECT * FROM USERS")
            print("SUCCESSFULLY SELECTED!")
            result = cursor.fetchall()
            print(result)
            return render_template("viewallusers.html", users=result, user_is_authenticated=True,
                                   username=session['name'])
        except Exception as e:
            print(e)


if __name__ == "__main__":
    socketio.run(app, debug=True)

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


# @auth.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get("email")
#         password = request.form.get("password")
#
#         user = User.query.filter_by(email=email).first()
#         if user:
#             if check_password_hash(user.password, password):
#                 flash("Logged in!", category='success')
#                 login_user(user, remember=True)
#                 return redirect(url_for('views.home'))
#             else:
#                 flash('Password is incorrect.', category='error')
#         else:
#             flash('Email does not exist.', category='error')
#
#     return render_template("login.html", user=current_user)


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


# @auth.route("/sign-up", methods=['GET', 'POST'])
# def sign_up():
#     if request.method == 'POST':
#         email = request.form.get("email")
#         username = request.form.get("username")
#         password1 = request.form.get("password1")
#         password2 = request.form.get("password2")
#
#         email_exists = User.query.filter_by(email=email).first()
#         username_exists = User.query.filter_by(username=username).first()
#
#         if email_exists:
#             flash('Email is already in use.', category='error')
#         elif username_exists:
#             flash('Username is already in use.', category='error')
#         elif password1 != password2:
#             flash('Password don\'t match!', category='error')
#         elif len(username) < 2:
#             flash('Username is too short.', category='error')
#         elif len(password1) < 6:
#             flash('Password is too short.', category='error')
#         elif len(email) < 4:
#             flash("Email is invalid.", category='error')
#         else:
#             new_user = User(email=email, username=username, password=generate_password_hash(
#                 password1, method='sha256'))
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user, remember=True)
#             flash('User created!')
#             return redirect(url_for('views.home'))
#
#     return render_template("signup.html", user=current_user)


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


# @views.route("/")
# @views.route("/home")
# @login_required
# def home():
#     posts = Post.query.all()
#     #fetch kr sarv ani display kr
#     return render_template("home.html", user=current_user, posts=posts)

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


# @views.route("/create-post", methods=['GET', 'POST'])
# @login_required
# def create_post():
#     if request.method == "POST":
#         text = request.form.get('text')
#
#         if not text:
#             flash('Post cannot be empty', category='error')
#         else:
#             post = Post(text=text, author=current_user.id)
#             db.session.add(post)
#             db.session.commit()
#             flash('Post created!', category='success')
#             return redirect(url_for('views.home'))
#
#     return render_template('create_post.html', user=current_user)
#
#
# @views.route("/delete-post/<id>")
# @login_required
# def delete_post(id):
#     post = Post.query.filter_by(id=id).first()
#
#     if not post:
#         flash("Post does not exist.", category='error')
#     elif current_user.id != post.id:
#         flash('You do not have permission to delete this post.', category='error')
#     else:
#         db.session.delete(post)
#         db.session.commit()
#         flash('Post deleted.', category='success')
#
#     return redirect(url_for('views.home'))
#
#
# @views.route("/posts/<username>")
# @login_required
# def posts(username):
#     user = User.query.filter_by(username=username).first()
#
#     if not user:
#         flash('No user with that username exists.', category='error')
#         return redirect(url_for('views.home'))
#
#     posts = user.posts
#     return render_template("posts.html", user=current_user, posts=posts, username=username)
#
#
# @views.route("/create-comment/<post_id>", methods=['POST'])
# @login_required
# def create_comment(post_id):
#     text = request.form.get('text')
#
#     if not text:
#         flash('Comment cannot be empty.', category='error')
#     else:
#         post = Post.query.filter_by(id=post_id)
#         if post:
#             comment = Comment(
#                 text=text, author=current_user.id, post_id=post_id)
#             db.session.add(comment)
#             db.session.commit()
#         else:
#             flash('Post does not exist.', category='error')
#
#     return redirect(url_for('views.home'))
#
#
# @views.route("/delete-comment/<comment_id>")
# @login_required
# def delete_comment(comment_id):
#     comment = Comment.query.filter_by(id=comment_id).first()
#
#     if not comment:
#         flash('Comment does not exist.', category='error')
#     elif current_user.id != comment.author and current_user.id != comment.post.author:
#         flash('You do not have permission to delete this comment.', category='error')
#     else:
#         db.session.delete(comment)
#         db.session.commit()
#
#     return redirect(url_for('views.home'))
#
#
# @views.route("/like-post/<post_id>", methods=['POST'])
# @login_required
# def like(post_id):
#     post = Post.query.filter_by(id=post_id).first()
#     like = Like.query.filter_by(
#         author=current_user.id, post_id=post_id).first()
#
#     if not post:
#         return jsonify({'error': 'Post does not exist.'}, 400)
#     elif like:
#         db.session.delete(like)
#         db.session.commit()
#     else:
#         like = Like(author=current_user.id, post_id=post_id)
#         db.session.add(like)
#         db.session.commit()
#
#     return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
#


if __name__ == "__main__":
    app.run()

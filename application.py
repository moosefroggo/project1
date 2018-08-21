from flask import Flask, session, request, render_template, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Set up goodreads api key
api_key = "Q0mLjb2BiiVV2k1KAASYWA"

@app.route("/")
def index():
    #Login check
    logged_in = is_logged_in()
    return render_template("index.html", logged_in = logged_in)
@app.route("/logout")
def logout():
    session.pop("username", None)
    return(redirect(url_for('index')))
@app.route("/registration", methods = ["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or username is "":
            return render_template('registration.html', message="username cannot be empty")
        if password is None or password is "":
            return render_template('registration.html', message="password cannot be empty")
        if user_exists(username):
            return redirect(url_for('login'))
        else:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
            print(password)
            db.commit()
            # parameter = {"username": username, "password": password}
            # db.execute(query, parameter)
            return "REGISTERED"
    else:
        if is_logged_in():
            return(redirect(url_for('index')))
        return render_template('registration.html')

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None or username is "":
            return render_template('registration.html', message="username cannot be empty")
        if password is None or password is "":
            return render_template('registration.html', message="password cannot be empty")
        if user_exists(username):
            query = "SELECT password FROM users WHERE username = :username"
            param = {"username": username}
            query_result = db.execute(query, param).fetchone()
            pass_from_db = query_result[0]
            print(pass_from_db)
            if pass_from_db == password:                
                session["username"] = username
                return "Logged In"
            else:
                message = "Password is incorrect"
                return render_template("login.html", message=message)
        else:
            message = "user does not exist"
            return render_template("login.html", message = message)
    else:
        if is_logged_in():
            return redirect(url_for('index'))
        return render_template("login.html")

@app.route("/search", methods = ["POST"])
def search():
    search_input = request.form.get("query")
    db_query = 'SELECT * from books WHERE title ILIKE %s'
    args = {'search_input': search_input}
    s = '%' + search_input + '%'
    books = db.bind.execute(db_query, s).fetchall()
    # db.execute(db_query, args).fetchone()
    return render_template('books.html', books = books)

@app.route("/book/<isbn>")
def book(isbn):
    query = 'SELECT * from books where isbn = :isbn'
    param = {'isbn': isbn}
    book_result = db.execute(query,param).fetchone()
    print(book_result['title'])
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn})
    goodreads_data = res.json()
    book_data = goodreads_data["books"]
    return render_template('book.html', book_result = book_result, book_data = book_data)
def user_exists(username):
    query = "SELECT * from users WHERE username = :username"
    param = {"username": username}
    if db.execute(query, param).rowcount > 0:
        return True
    else:
        return False
def is_logged_in():
    if 'username' in session:
        return True
    else:
        return False
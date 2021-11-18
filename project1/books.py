import os, json

from flask import Flask, session,render_template,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import request,flash,redirect,Response
from loginn import login_required
import requests

app = Flask(__name__)


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    return render_template('welcome.html',name=user_id)

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login")
def login():
    session.clear()
    return render_template('login.html')

@app.route("/register")
def register():
    session.clear()
    return render_template('register.html')

@app.route("/errorp")
def errorp():
    return render_template('error.html',message="Login First!")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/home")

@app.route("/signup" ,methods=["POST","GET"])
def signup():
    session.clear()
    if request.method == "POST":
        user_id = request.form.get("userid")
        password = request.form.get("password")
        if user_id.isalpha():
            if db.execute("SELECT * from users WHERE userid = :userid",{"userid":user_id}).rowcount == 1:
                return render_template('error.html', message="User Id aldready exists, try another one ")
            db.execute ("INSERT INTO Users (userid,password) VALUES (:userid, :password)",
                    {"userid":user_id, "password": password})
            db.commit()
            return render_template('success.html',message="Registered!")
        return render_template('error.html', message="Invalid User ID, Only alphabets please ;)")
        return redirect("/login")
    return render_template('register.html')

@app.route("/welcome",methods=["POST","GET"])
def welcome():
    session.clear()
    if request.method == "POST":
        user_id = request.form.get("userid")
        if not user_id.isalpha():
            return render_template('error.html',message="User id must contain only alphabets")
        password = request.form.get("password")
        rows = db.execute("SELECT * from users WHERE userid = :userid AND password = :password",{"userid":user_id, "password":password})
        result = rows.fetchone()
        if rows == 0:
            return render_template('error.html',message="Invalid Credentials")
        session["user_id"] = result[0]
        session["user_name"] = result[1]
        return redirect("/")
    else:
        return render_template('login.html')

@app.route("/vbooks", methods=["POST","GET"])
@login_required
def vbooks():
    books = db.execute("SELECT * from books").fetchall()
    return render_template('sbooks.html',books=books)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/vbooks/<string:book_id>")
@login_required
def book(book_id):
    book = db.execute("SELECT * from books WHERE isbn = :isbn",{"isbn":book_id}).fetchone()
    if book is None:
        return render_template('error.html',message="No books found!")
    review = db.execute("SELECT rating,comment FROM reviews WHERE isbn = :isbn",{"isbn":book_id}).fetchall()
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "mfhdkoo5ZcH9Fqg84egMmQ", "isbns": book_id})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']
        return render_template('rvbook.html', book=book,reviews=review, average_rating = average_rating, work_ratings_count = work_ratings_count)
    except:
         return render_template('rvbook.html', book=book,reviews=review)

@app.route("/rvwbook/<isbn>", methods=["GET","POST"])
@login_required
def rvwbook(isbn):
    if request.method == "POST":
        currentUser = session["user_id"]
        comment = request.form.get("breview")
        rating = request.form.get("bstars")

        row = db.execute("SELECT isbn FROM books WHERE isbn = :isbn",{"isbn": isbn})

        bookId = row.fetchone() 
        bookId = bookId[0]

        row2 = db.execute("SELECT * FROM reviews WHERE userid = :userid AND isbn = :isbn",{"userid": currentUser,"isbn": bookId})
        if row2.rowcount == 1:
            flash('You already submitted a review for this book', 'warning')
            return redirect("/vbooks/" + isbn)
    
        rating = str(rating)

        db.execute("INSERT INTO reviews (userid, isbn, comment, rating) VALUES (:userid, :isbn, :comment, :rating)",
            {"userid": currentUser, "isbn": bookId, "comment": comment, "rating": rating})
        db.commit()

        flash('Review submitted!', 'info')

        return redirect("/vbooks/" + isbn)

    return redirect("/")


@app.route("/api/<string:isbn>")
def api(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    if data is None:
        return render_template('error.html',message="404 Not Found")
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "mfhdkoo5ZcH9Fqg84egMmQ", "isbns": isbn})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    x = {
    "title": data.name,
    "author": data.author,
    "year": data.year,
    "isbn": isbn,
    "review_count": work_ratings_count,
    "average_score": average_rating
    }
    api=json.dumps(x)
    return render_template("api.json",api=api)
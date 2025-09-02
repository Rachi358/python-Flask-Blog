from flask import (
    Flask, render_template, request, session, redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mail import Mail
import os, json, math
from dotenv import load_dotenv

# ------------------------
# Load environment & config
# ------------------------
load_dotenv()

# Load UI/public params from config.json
with open("config.json", "r", encoding="utf-8") as f:
    params = json.load(f)["params"]

# Override with secrets from .env
params["admin_username"] = os.getenv("ADMIN_USERNAME", "")
params["admin_password"] = os.getenv("ADMIN_PASSWORD", "")
params["gmail_user"] = os.getenv("GMAIL_USER", "")
params["gmail_pass"] = os.getenv("GMAIL_PASS", "")

# ------------------------
# App / Config
# ------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# Mail
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params.get("gmail_user", ""),
    MAIL_PASSWORD=params.get("gmail_pass", ""),
    MAIL_SUPPRESS_SEND=False
)
mail = Mail(app)

# Database (Render will provide DATABASE_URL, fallback to SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///blog.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Uploads
UPLOAD_FOLDER = params.get("upload_folder", "static/uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# Models
# ------------------------
class Contact(db.Model):
    sr_no: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column()
    phone_no: Mapped[str] = mapped_column()
    msg: Mapped[str] = mapped_column()
    date: Mapped[datetime] = mapped_column(default=datetime.now)

class Posts(db.Model):
    sr_no: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    content: Mapped[str] = mapped_column()
    tagline: Mapped[str] = mapped_column()
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    img_file: Mapped[str] = mapped_column(nullable=True)

with app.app_context():
    db.create_all()

# ------------------------
# Helpers
# ------------------------
def is_admin_logged_in() -> bool:
    return session.get("user") == params["admin_username"]

@app.context_processor
def inject_globals():
    return {"params": params, "year": datetime.now().year}

# ------------------------
# Routes
# ------------------------
@app.route("/")
def index():
    page = request.args.get("page", default=1, type=int)
    per_page = int(params.get("no_of_posts", 5))
    total = Posts.query.count()
    last_page = max(1, math.ceil(total / per_page))
    page = min(max(1, page), last_page)

    posts = (
        Posts.query
        .order_by(Posts.date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    prev_url = url_for("index", page=page - 1) if page > 1 else None
    next_url = url_for("index", page=page + 1) if page < last_page else None

    return render_template(
        "index.html",
        posts=posts, prev=prev_url, next=next_url,
        page=page, last_page=last_page, total=total
    )

@app.route("/post/<string:post_slug>")
def post(post_slug):
    post_obj = Posts.query.filter_by(slug=post_slug).first_or_404()
    return render_template("post.html", post=post_obj)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone_no = request.form.get("phone", "").strip()
        msg = request.form.get("msg", "").strip()

        entry = Contact(name=name, email=email, phone_no=phone_no, msg=msg, date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        try:
            if params.get("gmail_user") and params.get("gmail_pass"):
                mail.send_message(
                    subject=f"New Message from {name}",
                    sender=email or params["gmail_user"],
                    recipients=[params["gmail_user"]],
                    body=f"Name: {name}\nEmail: {email}\nPhone: {phone_no}\n\nMessage:\n{msg}",
                )
        except Exception as e:
            app.logger.warning(f"Mail send failed: {e}")

        flash("Thanks! Your message has been sent.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == params.get("admin_username") and password == params.get("admin_password"):
            session["user"] = username
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ---------- Admin ----------
@app.route("/dashboard")
def dashboard():
    if not is_admin_logged_in():
        return redirect(url_for("login"))
    posts = Posts.query.order_by(Posts.date.asc()).all()
    return render_template("dashboard.html", posts=posts)

@app.route("/edit/<string:sr_no>", methods=["GET", "POST"])
def edit(sr_no):
    if not is_admin_logged_in():
        return redirect(url_for("login"))

    post = None if sr_no == "0" else Posts.query.get_or_404(sr_no)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        content = request.form.get("content", "").strip()
        tagline = request.form.get("tagline", "").strip()
        img_file = request.form.get("img_file", "").strip()

        if sr_no == "0":
            post = Posts(title=title, slug=slug, content=content, tagline=tagline, img_file=img_file)
            db.session.add(post)
        else:
            post.title = title
            post.slug = slug
            post.content = content
            post.tagline = tagline
            post.img_file = img_file

        db.session.commit()
        flash("Post saved successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit.html", post=post)

@app.route("/delete/<int:sr_no>", methods=["POST"])
def delete(sr_no):
    if not is_admin_logged_in():
        return redirect(url_for("login"))
    post = Posts.query.get_or_404(sr_no)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "info")
    return redirect(url_for("dashboard"))

# --- Uploads ---
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not is_admin_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("file1")
        if not file or file.filename == "":
            flash("No file selected.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        flash("Uploaded successfully.", "success")
        return redirect(url_for("dashboard"))

    return """ <form method="post" enctype="multipart/form-data">
    <input type="file" name="file1"> <button type="submit">Upload</button> 
    </form> """

# ---------- Search ----------
@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        like = f"%{q}%"
        results = (
            Posts.query.filter(
                (Posts.title.ilike(like)) |
                (Posts.tagline.ilike(like)) |
                (Posts.content.ilike(like))
            ).order_by(Posts.date.desc()).all()
        )
    return render_template("search.html", q=q, results=results)

# ---------- Errors ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)











# from flask import Flask, render_template, request, session, redirect
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import Mapped, mapped_column
# from datetime import datetime
# import json
# from flask_mail import Mail
# import os
# from werkzeug.utils import secure_filename
# import math

# # Load config.json
# local_server = True
# with open('config.json', 'r') as c:
#     params = json.load(c)['params']

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = params['upload_location']

# app.secret_key = 'the-random-string' # Set a secret key for session management

# # Flask-Mail configuration
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT=465,
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail_user'],
#     MAIL_PASSWORD=params['gmail_pass']
# )
# mail = Mail(app)

# # Database configuration
# if local_server:
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
# else:
#     app.config["SQLALCHEMY_DATABASE_URI"] = params['production_uri']

# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# # Initialize DB
# db = SQLAlchemy(app)


# # Contact model
# class Contact(db.Model):
#     sr_no: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(nullable=False)
#     email: Mapped[str] = mapped_column()
#     phone_no: Mapped[str] = mapped_column()
#     msg: Mapped[str] = mapped_column()
#     date: Mapped[datetime] = mapped_column(default=datetime.now)


# # Posts model
# class Posts(db.Model):
#     sr_no: Mapped[int] = mapped_column(primary_key=True)
#     title: Mapped[str] = mapped_column(nullable=False)
#     slug: Mapped[str] = mapped_column(nullable=False, unique=True)
#     content: Mapped[str] = mapped_column()
#     tagline: Mapped[str] = mapped_column()
#     date: Mapped[datetime] = mapped_column(default=datetime.now)
#     img_file: Mapped[str] = mapped_column(nullable=True)


# # Create tables if not exist
# with app.app_context():
#     db.create_all()


# # Routes
# @app.route("/")
# def index():
#     all_posts = Posts.query.all()
#     no_of_posts = int(params['no_of_posts'])
#     last = math.ceil(len(all_posts) / int(params['no_of_posts']))
#     if len(all_posts) % no_of_posts != 0:
#         last = last + 1

#     # get page number
#     page = request.args.get('page')
#     if (not str(page).isnumeric()):
#         page = 1
#     page = int(page)

#     # slicing posts
#     posts = all_posts[(page - 1) * no_of_posts : (page - 1) * no_of_posts + no_of_posts]

#     # pagination logic
#     if page == 1:
#         prev = "#"
#         next = "/?page=" + str(page + 1)
#     elif page == last:
#         prev = "/?page=" + str(page - 1)
#         next = "#"
#     else:
#         prev = "/?page=" + str(page - 1)
#         next = "/?page=" + str(page + 1)

#     return render_template("index.html", params=params, posts=posts, prev=prev, next=next)


# @app.route("/edit/<string:sr_no>", methods=['GET', 'POST'])
# def edit(sr_no): 
#     if 'user' in session and session['user'] == params['admin_username']:
#         if request.method == "POST":
#             title = request.form.get('title')
#             slug = request.form.get('slug')
#             content = request.form.get('content')
#             tagline = request.form.get('tagline')
#             img_file = request.form.get('img_file')
#             date = datetime.now()
#             if sr_no == '0':  
#                 # Create new post
#                 post = Posts(
#                     title=title,
#                     slug=slug,
#                     content=content,
#                     tagline=tagline,
#                     img_file=img_file,
#                     date = datetime.now()
#                 )
#                 db.session.add(post)
#             else:
#                 # Update existing post
#                 post = Posts.query.filter_by(sr_no=sr_no).first()
#                 post.title = title
#                 post.slug = slug
#                 post.content = content
#                 post.tagline = tagline
#                 post.date = date
#                 post.img_file = img_file

#             db.session.commit()
#             return redirect('/edit/' + sr_no)

#         post = None if sr_no == '0' else Posts.query.filter_by(sr_no=sr_no).first()
#         return render_template('edit.html', post=post, params=params)
    

# @app.route("/uploader", methods=['GET', 'POST']) 
# def uploader():
#     if 'user' in session and session['user'] == params['admin_username']:
#         if request.method == "POST":
#             f = request.files['file1']
#             f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
#             return "Uploaded successfully"
            

# @app.route("/logout") 
# def logout():
#     session.pop('user')
#     return redirect('/login')


# @app.route("/delete/<string:sr_no>", methods=['GET', 'POST'])
# def delete(sr_no):
#     if 'user' in session and session['user'] == params['admin_username']:
#         post = Posts.query.filter_by(sr_no = sr_no).first()
#         db.session.delete(post)
#         db.session.commit()
#     return redirect('/login')




# @app.route("/login", methods=['GET', 'POST'])  
# def login():
#     if request.method == "POST":
#         username = request.form.get("username")
#         password = request.form.get("password")

#         if username == params['admin_username'] and password == params['admin_password']:
#             session['user'] = username
#             posts = Posts.query.all()
#             return render_template('dashboard.html', params=params, posts=posts)

#         return render_template("login.html", params=params, error="Invalid username or password")

#     return render_template("login.html", params=params)
 

# @app.route("/about")
# def about():
#     return render_template('about.html', params=params)


# @app.route("/post/<string:post_slug>", methods=['GET'])
# def post(post_slug):
#     post = Posts.query.filter_by(slug=post_slug).first()
#     if not post:
#         return "Post not found", 404
#     return render_template('post.html', post=post, params=params)

# # @app.route("/post")
# # def all_posts():
# #     posts = Posts.query.all()
# #     return render_template("All_Posts.html", posts=posts, params=params)




# @app.route("/contact", methods=['GET', 'POST'])
# def contact():
#     if request.method == 'POST':
#         # Get form values
#         name = request.form.get('name')
#         email = request.form.get('email')
#         phone_no = request.form.get('phone')
#         msg = request.form.get('msg')

#         # Save entry to DB
#         entry = Contact(
#             name=name,
#             email=email,
#             phone_no=phone_no,
#             msg=msg,
#             date=datetime.now()
#         )
#         db.session.add(entry)
#         db.session.commit()

#         # Send email notification
#         mail.send_message(
#             subject='New Message from ' + name,
#             sender=email,
#             recipients=[params['gmail_user']],
#             body=f"Name: {name}\nEmail: {email}\nPhone: {phone_no}\n\nMessage:\n{msg}"
#         )

#     return render_template('contact.html', params=params)

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html', params=params), 404

# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html', params=params), 500

# if __name__ == "__main__":
#     app.run(debug=True)

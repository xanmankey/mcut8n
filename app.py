from datetime import timedelta
import os

from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField
from flask_admin.contrib.sqla import ModelView
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    render_template,
    url_for,
    g,
    session,
)
from flask_htmx import HTMX
from dotenv import load_dotenv
import sqlite3
from models.admin_users import AdminUsers
from models.event import Event
from models.gallery import Gallery
from models.rating import Rating
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from utils import Base
import random

if not load_dotenv(os.path.join(os.getcwd(), ".env")):
    print("No .env file found")
    exit()

app = Flask(__name__)
htmx = HTMX(app)
DB_PATH = "data.db"
BASE_PATH = os.path.join("static", "imgs")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

sqlalchemy_db = SQLAlchemy(app)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# Flask admin setup
admin = Admin(app, name="MCUT 8N", template_mode="bootstrap4")


class EventView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=BASE_PATH,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class GalleryView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False

    form_extra_fields = {
        "img": FileUploadField(
            "Image",
            base_path=BASE_PATH,
            allowed_extensions=["png", "jpg", "jpeg", "webp"],
        ),
    }


class RatingView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False


class AdminUsersView(ModelView):
    def is_accessible(self):
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        if (
            session.get("username") == admin_username
            and session.get("password") == admin_password
        ):
            return True
        return False


with app.app_context():
    # Configure the sqlite3 db
    # Create the events table if it doesn't exist
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, description TEXT, img BLOB, suggested BOOLEAN, rating INTEGER)"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS gallery (id INTEGER PRIMARY KEY, img BLOB, event INTEGER, FOREIGN KEY(event) REFERENCES events(id))"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS ratings (id INTEGER PRIMARY KEY, username TEXT, score INTEGER, event INTEGER, FOREIGN KEY(event) REFERENCES events(id))"
    # )
    # cur.execute(
    #     "CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
    # )
    # Create the tables if they don't exist
    Base.metadata.create_all(sqlalchemy_db.engine)
    # Create the admin user if it doesn't exist
    if not sqlalchemy_db.session.query(AdminUsers).first():
        admin_user = AdminUsers(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        sqlalchemy_db.session.add(admin_user)
        sqlalchemy_db.session.commit()
    admin.add_view(EventView(Event, sqlalchemy_db.session))
    # Generic model view for genres, forms, and artists
    admin.add_view(GalleryView(Gallery, sqlalchemy_db.session))
    admin.add_view(RatingView(Rating, sqlalchemy_db.session))
    admin.add_view(AdminUsersView(AdminUsers, sqlalchemy_db.session))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    counter = 0
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin_username = sqlalchemy_db.session.query(AdminUsers.username).first()[0]
        print(admin_username)
        admin_password = sqlalchemy_db.session.query(AdminUsers.password).first()[0]
        print(admin_password)

        if username == admin_username and password == admin_password:
            session["username"] = username
            session["password"] = password
            print("Redirecting to admin")
            return redirect("/admin")
        else:
            counter += 1
            if counter == 3:
                return redirect("/")
            return render_template("admin_login.html")
    elif request.method == "GET":
        return render_template("admin_login.html")


@app.route("/admin/logout", methods=["GET", "POST"])
def admin_logout():
    session.pop("username", None)
    session.pop("password", None)
    return redirect("/")


# Configure session
@app.before_request
def make_session_permanent():
    session.permanent = True
    # Make the session last for a year
    app.permanent_session_lifetime = timedelta(days=365)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def home():
    # Get all events that are not suggested
    events = sqlalchemy_db.session.query(Event).filter_by(suggested=False).all()
    random_event = random.choice(events)
    return render_template("index.html", event=random_event)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("events"))


@app.route("/events")
def events():
    if not session.get("username"):
        return redirect(url_for("login"))
    username = session.get("username")
    # Create a dictionary of {event_id: rating}; if there is no rating, set it to 0
    events = sqlalchemy_db.session.query(Event).order_by(Event.rating.desc()).all()
    events_dict = {}
    for event in events:
        events_dict[event] = event.rating
    return render_template("events.html", events=events_dict, username=username)


@app.route("/event/<int:id>")
def event(id):
    event = sqlalchemy_db.session.query(Event).get(id)
    if event:
        title = event.title
        description = event.description
        img = event.img
    else:
        abort(404)
    return render_template(
        "event.html",
        title=title,
        description=description,
        img=img,
        date_time=event.date_time,
    )


@app.route("/rate_event/<int:rating>/<int:id>/<string:username>", methods=["POST"])
def rate_event(rating, id, username):
    rating_obj = (
        sqlalchemy_db.session.query(Rating)
        .filter_by(event=id, username=username)
        .first()[0]
    )
    if rating_obj:
        rating_obj.score = rating
    else:
        rating_obj = Rating(event=id, username=username, score=rating)
        sqlalchemy_db.session.add(rating_obj)
    sqlalchemy_db.session.commit()
    if rating == 1:
        return f"""
    <div class="p-4">
      <button
        class="absolute px-2 py-1 left-0 bottom-[2%] bg-gray-200 rounded-full hover:bg-white"
        id="thumbs_up_{{ loop.index }}"
        hx-post="/rate_event/1/{{ event_id }}/{{ username }}"
        hx-target="#thumbs_up_{{ loop.index }}"
      >
        <i class="far fa-thumbs-up text-blue-800"></i>
      </button>
      <h2 class="text-xl font-bold text-center">{{ event.title }}</h2>
      <button
        class="absolute px-2 py-1 right-0 bottom-[2%] bg-gray-200 rounded-full p-1 hover:bg-white"
        id="thumbs_down_{{ loop.index }}"
      >
        <i class="far fa-thumbs-down text-gray-500 hover:text-red-800"></i>
      </button>
    </div>
"""
    elif rating == -1:
        return """
        <div class="p-4">
      <button
        class="absolute px-2 py-1 left-0 bottom-[2%] bg-gray-200 rounded-full hover:bg-white"
        id="thumbs_up_{{ loop.index }}"
        hx-post="/rate_event/1/{{ event_id }}/{{ username }}"
        hx-target="#thumbs_up_{{ loop.index }}"
      >
        <i class="far fa-thumbs-up text-gray-500 hover:text-blue-800"></i>
      </button>
      <h2 class="text-xl font-bold text-center">{{ event.title }}</h2>
      <button
        class="absolute px-2 py-1 right-0 bottom-[2%] bg-gray-200 rounded-full p-1 hover:bg-white"
        id="thumbs_down_{{ loop.index }}"
        hx-post="/rate_event/-1/{{ event_id }}/{{ username }}"
        hx-target="#thumbs_up_{{ loop.index }}"
      >
        <i class="far fa-thumbs-down text-gray-500 hover:text-red-800"></i>
      </button>
    </div>
"""
    else:
        return """
<div class="p-4">
      <button
        class="absolute px-2 py-1 left-0 bottom-[2%] bg-gray-200 rounded-full hover:bg-white"
        id="thumbs_up_{{ loop.index }}"
        hx-post="/rate_event/1/{{ event_id }}/{{ username }}"
        hx-target="#thumbs_up_{{ loop.index }}"
      >
        <i class="far fa-thumbs-up text-gray-500 hover:text-blue-800"></i>
      </button>
      <h2 class="text-xl font-bold text-center">{{ event.title }}</h2>
      <button
        class="absolute px-2 py-1 right-0 bottom-[2%] bg-gray-200 rounded-full p-1 hover:bg-white"
        id="thumbs_down_{{ loop.index }}"
        hx-post="/rate_event/-1/{{ event_id }}/{{ username }}"
        hx-target="#thumbs_up_{{ loop.index }}"
      >
        <i class="far fa-thumbs-down text-red-800"></i>
      </button>
    </div>
"""


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/create_event", methods=["GET", "POST"])
def create_event():
    if request.method == "GET":
        return render_template("create_event.html")
    elif request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        img = request.files.get("image", "").read()
        event = Event(
            title=title, description=description, img=img, suggested=True, rating=1
        )
        sqlalchemy_db.session.add(event)
        sqlalchemy_db.session.commit()
        return redirect(url_for("events"))


@app.route("/upload_gallery_img", methods=["GET", "POST"])
def upload_gallery_img():
    if request.method == "GET":
        return render_template("upload_gallery.html")
    elif request.method == "POST":
        img = request.files.get("image", "").read()
        event = request.form["event"]
        session = sqlalchemy_db.session
        gallery = Gallery(img=img, event=event)
        session.add(gallery)
        session.commit()

        return redirect(url_for("gallery"))


if __name__ == "__main__":
    app.run(debug=True)

from datetime import timedelta
import os

from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField, Select2Field
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

# if not load_dotenv(os.path.join(os.getcwd(), ".env")):
#     print("No .env file found")
#     exit()
load_dotenv()

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

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()

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

    @property
    def column_list(self):
        return ["id", "event_id"] + self.scaffold_list_columns()

    with app.app_context():
        form_extra_fields = {
            "img": FileUploadField(
                "Image",
                base_path=BASE_PATH,
                allowed_extensions=["png", "jpg", "jpeg", "webp"],
            ),
            "event_id": Select2Field(
                "Event",
                choices=[
                    (event.id, event.title)
                    for event in sqlalchemy_db.session.query(Event).all()
                ],
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

    @property
    def column_list(self):
        return ["id", "event_id"] + self.scaffold_list_columns()


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

    @property
    def column_list(self):
        return ["id"] + self.scaffold_list_columns()


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
    gallery = sqlalchemy_db.session.query(Gallery).all()
    random_gallery = random.choice(gallery)
    return render_template("index.html", event=random_event, gallery=random_gallery)


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
    # Create a dictionary of {id: rating}; if there is no rating, set it to 0
    events = (
        sqlalchemy_db.session.query(Event)
        .filter_by(suggested=False)
        .order_by(Event.date_time.asc())
        .all()
    )
    # Make the events without a date or time at the end
    events.sort(key=lambda x: x.date_time is None)
    # Order the suggested events (no date time) by rating
    suggested_events = (
        sqlalchemy_db.session.query(Event)
        .filter_by(suggested=True)
        .order_by(Event.rating.desc())
        .all()
    )
    # Combine the two lists
    events.extend(suggested_events)
    events_dict = {}
    for event in events:
        try:
            rating = (
                sqlalchemy_db.session.query(Rating)
                .filter_by(event_id=event.id, username=username)
                .first()
            )
            events_dict[event] = rating.score
            if rating.score == -1:
                print("Rating is -1")
        except Exception as e:
            events_dict[event] = 0
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


@app.route(
    "/rate_event/<int(signed=True):rating>/<int:id>/<string:username>", methods=["GET"]
)
def rate_event(rating, id, username):
    event = sqlalchemy_db.session.query(Event).filter_by(id=id).first()
    print(rating)
    print(id)
    if not event:
        abort(404)
    else:
        # Try and find an existing rating and update it
        rating_obj = (
            sqlalchemy_db.session.query(Rating)
            .filter_by(event_id=id, username=username)
            .first()
        )
        if rating_obj:
            # Update the user's rating and the event rating
            current_rating = rating_obj.score
            # If the ratings are the same, toggle the rating off (0)
            if current_rating == rating:
                rating_obj.score = 0
                event.rating -= current_rating
            else:
                rating_obj.score = rating
                event.rating += rating - current_rating
        else:
            # Create a new rating for the event
            rating_obj = Rating(event_id=id, username=username, score=rating)
            sqlalchemy_db.session.add(rating_obj)
            event.rating += rating
    sqlalchemy_db.session.commit()
    return redirect(url_for("events"))


@app.route("/gallery")
def gallery():
    gallery = sqlalchemy_db.session.query(Gallery).all()
    # Sort by event date descending
    print(gallery[0].event_id)
    gallery.sort(
        key=lambda x: (
            sqlalchemy_db.session.query(Event)
            .filter(Event.id == x.event_id)
            .first()
            .date_time
            if x.event_id
            else None
        ),
        reverse=True,
    )
    return render_template(
        "gallery.html", gallery=[gallery_inst.img for gallery_inst in gallery]
    )


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

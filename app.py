from datetime import timedelta
import os
import tempfile

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_htmx import HTMX
from dotenv import load_dotenv

# if not load_dotenv(os.path.join(os.getcwd(), ".env")):
#     print("No .env file found")
#     exit()

# SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
htmx = HTMX(app)

# # configure the SQLite database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = (
#     f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
# )
# app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

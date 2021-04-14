from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    flash,
    send_from_directory,
)
from flask.helpers import send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)

app = Flask(__name__)

app.config["SECRET_KEY"] = "any-secret-key-you-choose"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# config login manager
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# Line below only required once, when creating DB.
# db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if already email exist
        search_email = User.query.filter_by(email=request.form["email"])
        if search_email:
            flash("User already exist, try to login.")
            return redirect(url_for("login"))
        # creating and adding new user to the database
        new_user = User(
            email=request.form["email"],
            name=request.form["name"],
            # hash password
            password=generate_password_hash(
                request.form["password"], method="pbkdf2:sha256", salt_length=8
            ),
        )
        db.session.add(new_user)
        db.session.commit()

        # login the new user
        login_user(new_user)
        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # find user
        user = User.query.filter_by(email=email).first()
        # check email and password in db
        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details and try again.")
            return redirect(url_for("login"))

        login_user(user)
        return redirect(url_for("secrets"))
    return render_template("login.html")


@login_required
@app.route("/secrets")
def secrets():
    return render_template("secrets.html", name=current_user.name)


@login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_required
@app.route("/download")
def download():
    return send_from_directory(url_for("static"), filename="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)

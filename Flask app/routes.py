from init import app, bcrypt, db, login_manager
from flask import render_template, flash, redirect, url_for, request, session
from forms import RegistrationForm, LoginForm, MusicFilesForm
from database import User, MusicFiles
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from accepted_extensions import ACCEPTED_FILE_EXTENSIONS

# from io import BytesIO


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration
    Steps
        Pulls the entered data when 'register.html' is submitted.
        Stores it in the User table if email is unique.
        Redirects to the login page when user is created.
    Flashes
        red: if the user already exists
        green: When the account is created
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        is_creator = form.is_creator.data
        password_hash = bcrypt.generate_password_hash(form.password.data)
        if User.query.filter_by(email=email).first():
            flash("The user already exists", "red")
            return redirect(url_for("register"))
        user = User(
            username=username,
            email=email,
            password=password_hash,
            is_creator=is_creator,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account successfully created!", "green")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login
    Steps
        Logs the user in (stores the credentials of the user in the current context) if the user isn't logged in already
        Pulls the entered data when 'register.html' is submitted.
        Redirects to the home page by default.

    In case of a user wanting to access a page where login is required, the user is first redirected here and then to the respective page

    Flashes
        red: if the username or password doesn't match
        green: When the user successfully logs in
    """
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            flash(f"You're in: {current_user}", "green")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Failed. Check your email or password.", "red")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Logs the user out (removes current_user from the current context)"""
    logout_user()
    return redirect(url_for("home"))


@app.route("/upload_music", methods=["GET", "POST"])
@login_required
def input_music_files():
    form = MusicFilesForm()
    if form.validate_on_submit():
        file_data = form.music_file.data
        file_name = secure_filename(file_data.filename)
        file_extension = file_name.split(".")[1]
        # if MusicFiles.query.filter_by(title=form.title.data).first():
        #     flash("The nickname is taken. :(", "red")
        #     return redirect(url_for("input_music_files"))
        if file_extension not in ACCEPTED_FILE_EXTENSIONS:
            flash("Unsupported file", "red")
        else:
            musicfile = MusicFiles(
                file_name=secure_filename(file_name),
                file_data=file_data.read(),
                file_extension=file_extension,
                user_id=current_user.get_id(),
            )
            db.session.add(musicfile)
            db.session.commit()

    return render_template("musicsubmit.html", form=form)


@app.route("/button_clicked/<button_id>")
def button_clicked(button_id):
    session["instrument"] = button_id
    # print(button_id)
    return button_id


if __name__ == "__main__":
    app.run(debug=True)

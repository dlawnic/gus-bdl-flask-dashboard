from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import User
from .forms import RegisterForm, LoginForm

bp = Blueprint("auth", __name__)

@bp.get("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower().strip())
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Ten email jest już zarejestrowany.", "danger")
            return render_template("register.html", form=form)

        flash("Konto utworzone. Możesz się zalogować.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get("next") or url_for("dashboard.dashboard"))
        flash("Nieprawidłowy email lub hasło.", "danger")

    return render_template("login.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Wylogowano.", "info")
    return redirect(url_for("auth.login"))

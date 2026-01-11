from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=8, max=128)])
    password2 = PasswordField("Powtórz hasło", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Załóż konto")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Zaloguj")

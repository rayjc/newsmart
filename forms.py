from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import (URL, DataRequired, Email, InputRequired,
                                Length, Optional)


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField(
        'Username',
        validators=[DataRequired(), InputRequired(), Length(min=3)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), InputRequired(), Length(min=3)]
    )


class RegisterForm(FlaskForm):
    """Form for adding users."""
    username = StringField(
        'Username', validators=[DataRequired(), InputRequired(), Length(min=3)]
    )
    email = StringField(
        'E-mail', validators=[InputRequired(), DataRequired(), Email()]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), InputRequired(), Length(min=3)]
    )
    first_name = StringField(
        'First Name', validators=[DataRequired(), InputRequired()]
    )
    last_name = StringField(
        'Last Name', validators=[DataRequired(), InputRequired()]
    )


class UserEditForm(FlaskForm):
    """Form for editing users."""
    username = StringField(
        'Username',
        validators=[DataRequired(), InputRequired(), Length(min=3)]
    )
    password = PasswordField(
        'Verify Password',
        validators=[DataRequired(), InputRequired(), Length(min=3)]
    )
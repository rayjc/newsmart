from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField
from wtforms.validators import (URL, DataRequired, Email, InputRequired,
                                Length, Optional)


class ArticleForm(FlaskForm):
    """Form for adding articles."""
    title = StringField(
        'Title',
        validators=[DataRequired(), InputRequired()]
    )
    summary = StringField(
        'Summary',
        validators=[Optional()]
    )
    content = StringField(
        'Content',
        validators=[DataRequired(), InputRequired()]
    )
    url = StringField(
        'URL',
        validators=[DataRequired(), InputRequired(), URL()]
    )
    source = StringField(
        'Source',
        validators=[DataRequired(), InputRequired()]
    )
    img_url = StringField(
        'Image URL',
        validators=[Optional(), URL()]
    )
    timestamp = StringField(
        'Published At',
        validators=[DataRequired(), InputRequired()]
    )


class ArticleTagForm(FlaskForm):
    """Form for adding article-tag"""
    article_id = IntegerField(
        "Article id",
        validators=[DataRequired()]
    )
    tag_id = IntegerField(
        "Tag id",
        validators=[DataRequired()]
    )


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


class TagsForm(FlaskForm):
    """Form for adding tags."""
    article_url = StringField(
        "Article URL",
        validators=[DataRequired(), URL()]
    )

"""Models for NewSmart app."""
import datetime

from flask import flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from logger import logger

db = SQLAlchemy()

DEFAULT_IMG_URL = "static/image/question-mark.jpg"

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    saves = db.relationship('Saves', backref='user', passive_deletes=True)
    articles = db.relationship('Article', secondary="saves", lazy="joined",
                               backref='users')

    bcrypt = Bcrypt()

    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """
        Register user w/hashed password & commit to db.
        Return user object if successful, otherwise return None.
        """

        hashed = cls.bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        new_user =  cls(
            username=username, password=hashed_utf8, email=email,
            first_name=first_name, last_name=last_name
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("Username/email already exist.", "danger")
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(f'Failed to create {new_user} on database.')
            flash(f"Failed to create '{username}'", "danger")
            db.session.rollback()
            return None

        return new_user

    @classmethod
    def update(cls, old_username, new_username, password):
        """
        Update user with specified id & commit to db.
        Return user object if successful, otherwise return None.
        """
        user = User.authenticate(old_username, password)
        if not user:
            flash("Username and password do not match!", 'danger')
            return None
        
        user.username = new_username

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            flash("Username already exists.", "danger")
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(f'Failed to update {user} on database.')
            flash(f"Failed to update '{username}'", "danger")
            db.session.rollback()
            return None

        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """
        Validate that user exists & password is correct.
        Return user if valid; else return None.
        """

        user = cls.query.filter_by(username=username).first()

        if user and cls.bcrypt.check_password_hash(user.password, pwd):
            # return user instance
            return user
        else:
            return None

    def __repr__(self):
        return (f"<User: username='{self.username}' "
                f"email='{self.email}' "
                f"first_name={self.first_name} "
                f"last_name={self.last_name}>")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Article(db.Model):
    
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False, unique=True)
    source = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.Text, nullable=False, default=DEFAULT_IMG_URL)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.utcnow())

    saves = db.relationship('Saves', backref='article', passive_deletes=True)
    articles_tags = db.relationship('ArticleTag', backref='article', passive_deletes=True)

    @classmethod
    def new(cls, title, content, url, source, summary=None, img_url=None, timestamp=None):
        """
        Create new article object and commit to db.
        Return article object if successful, otherwise return None.
        Note: articles can only be added internally currently, no UI.
        """

        new_article = cls(
            title=title, summary=summary, content=content,
            url=url, source=source, img_url=img_url, timestamp=timestamp
        )

        try:
            db.session.add(new_article)
            db.session.commit()
        except IntegrityError:
            logger.error(f"Cannot add {new_article} to database; URL already exists.")
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(f'Failed to create {new_article} on database.')
            db.session.rollback()
            return None

        return new_article

    def __repr__(self):
        return (f"<Article: id={self.id} "
                f"title={self.title if len(self.title) < 20 else '...'} "
                f"url={self.url if len(self.url) < 20 else '...'} "
                f"source={self.source} "
                f"timestamp={self.timestamp} "
                f"has_summary={'yes' if self.summary else 'no'}>")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "img_url": self.img_url,
            "timestamp": self.timestamp.isoformat(),
        }


class Tag(db.Model):

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword = db.Column(db.String(32), nullable=False, unique=True)

    articles_tags = db.relationship('ArticleTag', backref='tag', passive_deletes=True)
    articles = db.relationship('Article', secondary="articles_tags", backref='tags')

    @classmethod
    def new(cls, keyword):
        """
        Create new tag object and commit to db.
        Return tag object if successful, otherwise return None.
        Note: tags can only be added internally, no UI.
        """

        new_tag = cls(keyword=keyword)

        try:
            db.session.add(new_tag)
            db.session.commit()
        except IntegrityError:
            logger.warning(
                f"Cannot add {new_tag} to database; URL already exists."
            )
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(f'Failed to create {new_tag} on database.')
            db.session.rollback()
            return None

        return new_tag

    def __repr__(self):
        return (f"<Tag: id={self.id} "
                f"keyword='{self.keyword}'>")
    
    def serialize(self):
        return {
            "id": self.id,
            "keyword": self.keyword,
        }


# Intermediate tables for many-to-many relationship
class Saves(db.Model):

    __tablename__ = "saves"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # delete record if any parents get removed
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    article_id = db.Column(db.Integer,
                           db.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

    __table_args__ = (
        db.UniqueConstraint('user_id', 'article_id', name='unique_bookmark'),
    )

    @classmethod
    def new(cls, user_id, article_id, timestamp=None):
        """
        Create new saves object and commit to db.
        Return saves object if successful, otherwise return None.
        Note: saves object can only be added internally, no UI.
        """

        new_saves = cls(user_id=user_id, article_id=article_id, timestamp=timestamp)

        try:
            db.session.add(new_saves)
            db.session.commit()
        except IntegrityError as e:
            logger.error(
                f"Cannot add {new_saves} to database. {e.orig.pgerror}"
            )
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(f'Failed to create {new_saves} on database.')
            db.session.rollback()
            return None

        return new_saves

    @classmethod
    def remove(cls, saves_id):
        """
        Remove saves object and commit to db.
        Return True if successful, otherwise return False.
        """
        saves = cls.query.get_or_404(saves_id)

        try:
            db.session.delete(saves)
            db.session.commit()
        except SQLAlchemyError:
            logger.critical(f'Failed to delete {saves} from database.')
            db.session.rollback()
            return False
        
        return True

    def __repr__(self):
        return (f"<Saves: user_id={self.user_id} article_id='{self.article_id}'>")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "article_id": self.article_id,
            "timestamp": self.timestamp.isoformat(),
        }


class ArticleTag(db.Model):

    __tablename__ = "articles_tags"

    # delete record if any parents get removed
    article_id = db.Column(db.Integer,
                           db.ForeignKey('articles.id', ondelete='CASCADE'),
                           primary_key=True)
    tag_id = db.Column(db.Integer,
                           db.ForeignKey('tags.id', ondelete='CASCADE'),
                           primary_key=True)

    @classmethod
    def new(cls, article_id, tag_id):
        """
        Create new article-tag object and commit to db.
        Return article-tag object if successful, otherwise return None.
        Note: article-tag object can only be added internally, no UI.
        """

        new_article_tag = cls(article_id=article_id, tag_id=tag_id)

        try:
            db.session.add(new_article_tag)
            db.session.commit()
        except IntegrityError:
            logger.error(
                f"Cannot add {new_article_tag} to database; URL already exists."
            )
            db.session.rollback()
            return None
        except SQLAlchemyError:
            logger.critical(
                f'Failed to create {new_article_tag} on database.')
            db.session.rollback()
            return None

        return new_article_tag

    def __repr__(self):
        return (f"<Article-Tag: article={self.article_id} tag_id='{self.tag_id}'>")
    

def connect_db(app):
    """
    Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

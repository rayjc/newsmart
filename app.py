import os

from flask import Flask, abort, Response, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from logger import logger
from models import connect_db

app = Flask(__name__)

# flask config setup
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///newsmart')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "test")
toolbar = DebugToolbarExtension(app)

connect_db(app)


@app.route('/')
def home_view():
    """
    Home page with viewable/hidden sections for authenicated users.
    """
    return Response("Home Page")


@app.route('/category')
def category_view():
    """
    Categories page showing list of available categories. (Optional)
    """
    return Response("List of available categories")


@app.route('/category/<string:category>')
def category_detail_view(category):
    """
    Category detail page showing list of top articles under specified category.
    """
    if (category.lower() not in ("business", "entertainment", "general",
                                 "health", "science", "sports", "technology")):
        abort(404)

    return Response(f"List of top articles under {category}")


@app.route('/search')
def search_view():
    """
    Search result page detailing the articles found with query parameter.
    """
    term = request.args.get('q')

    # TODO: SQLAlchemy-Searchable; update models
    # call search

    return Response(f"List of articles related to '{term}'")


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    """
    Login page for accepting login form submission.
    """

    # validate form

    # log user in via session
    
    return Response(f"Login form")


@app.route('/signup', methods=['GET', 'POST'])
def signup_view():
    """
    Sign up page for accepting signup form submission.
    """

    # validate form

    # create and register user

    # log user in via session

    return Response(f"Signup from")


@app.route('/user')
def user_profile_view(username, methods=['GET', 'POST']):
    """
    User profile page:
        -Shows user information
        -form for updating user info; could consider patch request via ajax
        -list of articles user has saved/bookmarked with keywords extracted
        (These article keywords are used for recommendation)
    """

    # validate data for patch request

    return Response("User profile form and saved articles")


# RESTful APIs
@app.route('/api/articles', methods=['POST'])
def create_article():
    """
    Create an article object and store on db.
    Return article object in JSON response.
    Data: title, content, url, source, summary, img_url
    """

    # make sure user is logged in

    # return 200 if article object has been created already

    # create new article object and save

    # extract keywords via 3rd party API
    # create tags and associate them with this article

    # return JSON response including article object
    return (jsonify({"article": {"message": "testing"}}), 201)


@app.route('/api/saves', methods=['POST'])
def create_bookmark():
    """
    Create a relationship row between user and article.
    Return JSON response.
    Data: user_id, article_id
    Note: the article should have been created
    """

    # make sure user is logged in

    # create saves object and save

    # return JSON response
    return (jsonify({"saves": {"message": "testing"}}), 201)


@app.route('/api/saves/<int:saves_id>', methods=['DELETE'])
def remove_bookmark(saves_id):
    """
    Remove a relationship row between user and article.
    Return a message in JSON response.
    """

    # make sure is logged in

    # remove bookmark from db

    # return JSON response
    return (jsonify({"message": "testing"}), 200)

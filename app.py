import os

from flask import (Flask, Response, abort, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from forms import (ArticleForm, ArticleTagForm, LoginForm, RegisterForm,
                   TagsForm, UserEditForm)
from logger import logger
from models import (NEWS_CATEGORIES, Article, ArticleTag, Saves, Tag, User,
                    UserCategory, connect_db)
from news_api_session import NewsApiSession
from nlu_api_session import NLUApiSession
from util import (CURR_USER_KEY, do_login, do_logout, get_bookmarked_urls,
                  login_required)

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

news_api = NewsApiSession()
nlp_api = NLUApiSession()


@app.before_request
def add_user_to_g():
    """
    If we're logged in, add curr user to Flask global before making
    any request so each request has access to current user object.
    Note: g is an application global context that lasts for
        one request/response cycle unlike the session which
        remains and persists for mulitple requests/respones.
    """
    g.user = (
        User.query.get(session[CURR_USER_KEY])
        if CURR_USER_KEY in session
        else None
    )


@app.route('/')
def home_view():
    """
    Home page with viewable/hidden sections for authenicated users.
    """
    top_articles = news_api.get_top_articles()
    bookmarked_urls = get_bookmarked_urls()

    return render_template(
        "home.html", top_articles=top_articles,
        bookmarked_urls=bookmarked_urls
    )


@app.route('/category')
def category_view():
    """
    Categories page showing list of available categories. (Optional)
    """
    return render_template('category.html', categories=NEWS_CATEGORIES)


@app.route('/category/<string:category>')
def category_detail_view(category):
    """
    Category detail page showing list of top articles under specified category.
    """
    if (category.lower() not in NEWS_CATEGORIES):
        abort(404)

    articles = news_api.get_top_articles(category=category)
    return render_template('category_detail.html', articles=articles, category=category)


@app.route('/search')
def search_view():
    """
    Search result page detailing the articles found with query parameter.
    """
    phrase = request.args.get('q')
    
    # do not allow empty search
    if not phrase:
        return redirect(url_for('home_view'))

    # call search
    articles = news_api.search_articles(phrase)

    bookmarked_urls = get_bookmarked_urls()

    return render_template(
        'search.html', phrase=phrase, articles=articles,
        bookmarked_urls=bookmarked_urls
    )


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    """
    Login page for accepting login form submission.
    """
    if g.user:
        return redirect(url_for('home_view'))

    form = LoginForm()

    # validate form
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('home_view'))

        flash("Username and password do not match!", 'danger')

    return render_template(
        'login.html', form=form, form_id="login-form", submit_button="Log in"
    )


@app.route('/logout')
def logout_view():
    """Handle logout of user."""
    do_logout()
    return redirect(url_for('login_view'))


@app.route('/signup', methods=['GET', 'POST'])
def signup_view():
    """
    Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """
    if g.user:
        return redirect(url_for('home_view'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User.register(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")

        return redirect("/")

    else:
        return render_template(
            'signup.html', form=form, form_id="signup-form", submit_button="Sign up!"
        )


@app.route('/user', methods=['GET', 'POST'])
@login_required('/login')
def user_profile_view():
    """
    User profile page:
        -Shows user information
        -form for updating user info; could consider patch request via ajax
        -list of articles user has saved/bookmarked with keywords extracted
        (These article keywords are used for recommendation)
    """
    form = UserEditForm(username=g.user.username)

    if form.validate_on_submit():
        user = User.update(g.user.username, form.username.data, form.password.data)
        if user:
            flash("Username updated.", "success")
        return redirect(url_for('user_profile_view'))

    bookmarks = g.user.articles

    return render_template(
        "user_profile.html", form=form, submit_button="Update", bookmarks=bookmarks
    )


# RESTful APIs
@app.route('/api/articles', methods=['POST'])
# @login_required(isJSON=True)  TODO: uncomment
def create_article():
    """
    Create an article object and store on db.
    Return article object in JSON response.
    Data: title, content, url, source, summary, img_url
    """
    data = request.json
    form = ArticleForm(**data, meta={'csrf': False})

    if form.validate():
        article = Article.query.filter(Article.url == form.url.data).one_or_none()
        if article:
            # article object has been created already
            return (jsonify({"article": article.serialize()}), 200)
        else:
            # create new article object and save
            new_article = Article.new(**form.data)
            return (jsonify({"article": new_article.serialize()}), 201)

    errors = {"errors": form.errors}
    return (jsonify(errors), 400)


@app.route('/api/saves', methods=['POST'])
# @login_required(isJSON=True)  TODO: uncomment
def create_bookmark():
    """
    Create a relationship row between user and article.
    Return JSON response.
    Data: article_id
    PRE: the article should have been created before
    """
    article_id = request.json.get('article_id')
    if article_id and isinstance(article_id, int):
        bookmark = Saves.new(g.user.id, article_id)
        return (
            (jsonify({"bookmark": bookmark.serialize()}), 201)
            if bookmark else
            (jsonify({
                "bookmark": 
                    {"message": ("Failed to create "
                                 f"<Bookmark: article_id={article_id}, "
                                 f"user_id={g.user.id}>.")
                    }
            }), 400)
        )

    return (
        jsonify({"errors": {"article_id": ["Please provide valid article_id"]}}),
        400
    )


@app.route('/api/saves/<int:saves_id>', methods=['DELETE'])
# @login_required(isJSON=True)  TODO: uncomment
def remove_bookmark(saves_id):
    """
    Remove a relationship row between user and article.
    Return a message in JSON response.
    """
    if Saves.remove(saves_id):
        return (jsonify(
            {"bookmark": {"message": "Deleted.", "id": saves_id}}
        ), 200)

    return (jsonify(
        {"bookmark": {"message": f"Failed to delete bookmark."}}
    ), 400)


@app.route('/api/tags', methods=['POST'])
# @login_required(isJSON=True)  TODO: uncomment
def create_tags():
    """
    Extract tags based on url and save them to database;
    return lists of tag objects created in JSON response.
    Data: article_url
    """
    data = request.json
    form = TagsForm(**data, meta={'csrf': False})

    if form.validate():
        # extract keywords via 3rd party API
        # TODO: disable button on frontend after click since this takes awhile
        terms_map = nlp_api.get_relevant_terms(form.article_url.data)
        keywords, concepts = terms_map['keywords'], terms_map['concepts']
        # create each tag and save to db
        tags = (Tag.new(term) for term in (keywords + concepts))
        tags = filter(lambda tag: tag is not None, tags)
        tags = list(map(lambda tag: tag.serialize(), tags))
        return (jsonify({"tags": tags}), 201)

    errors = {"errors": form.errors}
    return (jsonify(errors), 400)


@app.route('/api/articletag', methods=['POST'])
def create_article_tag():
    """
    Create association between specified article and tag;
    return created association object in JSON.
    Data: article_id, tag_id
    PRE: article and tag must have been created on db
    """
    data = request.json
    form = ArticleTagForm(**data, meta={'csrf': False})

    if form.validate():
        article_tag = ArticleTag.new(form.article_id.data, form.tag_id.data)
        return (
            (jsonify({"article-tag": article_tag.serialize()}), 201)
            if article_tag else
            (jsonify({"article-tag": {"message": "Failed to create article-tag"}}),
                400)
        )

    errors = {"errors": form.errors}
    return (jsonify(errors), 400)

"""Articles API tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/api/test_articles_api.py
#   python -m unittest discover tests/api/
# Note: This is necessary to avoid relative/absolute import based on path.

import os
import copy
import datetime
import logging
from contextlib import contextmanager
from unittest import TestCase

from flask import appcontext_pushed, g
from sqlalchemy.exc import IntegrityError

from util import CURR_USER_KEY

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///newsmart-test"

# Now we can import app
from app import app
from models import Article, User, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


class ArticleApiTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        Article.query.delete()
        User.query.delete()

        article = Article.new(
            "Secret", "Bruce Wayne is the Batman",
            "http://www.google.com",
            "The Joker"
        )
        user = User.register(
            "test", "raw_password", "test@test.com",
            "Test", "User"
        )
        # keep track of id reference instead of db reference
        # db session may get refreshed after modifying session...
        self.article_id = article.id
        self.user_id = user.id


    def tearDown(self):
        db.session.rollback()

    def test_get_article_by_url(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.get("/api/articles",
                            query_string={"article_url": "http://www.google.com"})
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)
        self.assertDictEqual(
            resp.get_json(),
            {"article": Article.query.get(self.article_id).serialize()}
        )

        with self.subTest("Missing query parameter"):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.get("/api/articles")

            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())

        with self.subTest("No article saved under such url"):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.get("/api/articles",
                                query_string={"article_url": "http://www.test.com"})

            self.assertEqual(resp.status_code, 404)

    def test_create_article(self):
        json = {
            "title": "Test Article",
            "summary": "Short summary",
            "content": "Some content",
            "url": "http://www.test.com",
            "source": "Google-News",
            "img_url": "https://source.unsplash.com/daily",
            "timestamp": datetime.datetime.today().isoformat(),
        }
        # test successful request
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.post("/api/articles" ,json=json)

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.is_json)
        json_resp = resp.get_json()
        self.assertIn("article", json_resp)
        del json_resp['article']['id']
        self.assertDictEqual(json, json_resp['article'])

        # test duplicate article url
        with self.subTest("Article url already exists"):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post("/api/articles", json=json)

            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.is_json)
            json_resp = resp.get_json()
            self.assertIn("article", json_resp)
            del json_resp['article']['id']
            self.assertDictEqual(json, json_resp['article'])

        # test missing data field
        for key in json:
            # skip the optional parameters
            if key in ("summary", "img_url", "timestamp"):
                continue
            temp = copy.deepcopy(json)
            del temp[key]   # remove one of the parameter

            with self.subTest(f"Missing {key}"):
                with app.test_client() as client:
                    with client.session_transaction() as sess:
                        sess[CURR_USER_KEY] = self.user_id
                    resp = client.post("/api/articles", json=temp)

                self.assertEqual(resp.status_code, 400)
                self.assertTrue(resp.is_json)
                self.assertIn("errors", resp.get_json())
                self.assertIn(key, resp.get_json()['errors'])


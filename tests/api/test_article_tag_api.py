"""Article-Tag API tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/api/test_article_tag_api.py
#   python -m unittest discover tests/api/
# Note: This is necessary to avoid relative/absolute import based on path.

import os
import copy
import datetime
import logging
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
from models import Tag, Article, ArticleTag, User, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


class ArticleTagApiTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        Tag.query.delete()
        Article.query.delete()
        User.query.delete()

        tag = Tag.new("Testing")
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
        self.tag_id = tag.id
        self.article_id = article.id
        self.user_id = user.id

    def tearDown(self):
        db.session.rollback()

    def test_create_article_tag(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.post(
                "/api/articletag",
                json={
                    "article_id": self.article_id,
                    "tag_id": self.tag_id,
                }
            )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.is_json)
        self.assertIn("articletag", resp.get_json())
        self.assertDictEqual(
            {"article_id": self.article_id, "tag_id": self.tag_id},
            resp.get_json()['articletag']
        )
        # test duplicate article-tag
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.post(
                "/api/articletag",
                json={
                    "article_id": self.article_id,
                    "tag_id": self.tag_id,
                }
            )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.is_json)
        self.assertIn("articletag", resp.get_json())
        self.assertIn("message", resp.get_json()['articletag'])

        with self.subTest("Missing article_id"):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/articletag",
                    json={
                        "tag_id": self.tag_id,
                    }
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("article_id", resp.get_json()['errors'])

        with self.subTest("Missing tag_id"):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/articletag",
                    json={
                        "article_id": self.article_id,
                    }
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("tag_id", resp.get_json()['errors'])

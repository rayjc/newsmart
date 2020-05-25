"""Saves/Bookmark API tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/api/test_saves_api.py
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
from models import Saves, Article, User, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


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
        # saves = Saves.new(user.id, article.id)

        # keep track of id reference instead of db reference
        # db session may get refreshed after modifying session...
        self.article_id = article.id
        self.user_id = user.id
        # self.saves_id = saves.id

    def tearDown(self):
        db.session.rollback()

    def test_create_bookmark(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.post(
                "/api/saves",
                json={
                    "article_id": self.article_id
                }
            )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.is_json)
        self.assertIn("bookmark", resp.get_json())
        self.assertIn("id", resp.get_json()['bookmark'])
        self.assertIn("user_id", resp.get_json()['bookmark'])
        self.assertIn("article_id", resp.get_json()['bookmark'])
        self.assertIn("timestamp", resp.get_json()['bookmark'])
        self.assertEqual(self.user_id, resp.get_json()['bookmark']['user_id'])
        self.assertEqual(self.article_id, resp.get_json()['bookmark']['article_id'])

        with self.subTest('Duplicate bookmark'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/saves",
                    json={
                        "article_id": self.article_id
                    }
                )
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.is_json)
            self.assertIn("bookmark", resp.get_json())
            self.assertIn("id", resp.get_json()['bookmark'])
            self.assertIn("user_id", resp.get_json()['bookmark'])
            self.assertIn("article_id", resp.get_json()['bookmark'])
            self.assertIn("timestamp", resp.get_json()['bookmark'])
            self.assertEqual(self.user_id, resp.get_json()['bookmark']['user_id'])
            self.assertEqual(self.article_id, resp.get_json()
                            ['bookmark']['article_id'])

        with self.subTest('No matching article_id'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/saves",
                    json={
                        "article_id": self.article_id + 1
                    }
                )
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(resp.is_json)
        self.assertIn("bookmark", resp.get_json())
        self.assertIn("message", resp.get_json()['bookmark'])

        with self.subTest('Missing article_id'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/saves",
                    json={}
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("article_id", resp.get_json()['errors'])

        with self.subTest('Invalid article_id'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.post(
                    "/api/saves",
                    json={
                        "article_id": str(self.article_id)
                    }
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("article_id", resp.get_json()['errors'])

    def test_remove_bookmark(self):
        saves = Saves.new(self.user_id, self.article_id)
        bookmark_id = saves.id
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.delete(f"/api/saves/{bookmark_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)
        self.assertIn("bookmark", resp.get_json())
        self.assertIn("id", resp.get_json()['bookmark'])
        self.assertIn("message", resp.get_json()['bookmark'])
        self.assertEqual(bookmark_id, resp.get_json()['bookmark']['id'])

        # test no matching bookmark_id
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.delete(f"/api/saves/{bookmark_id}")
        self.assertEqual(resp.status_code, 404)

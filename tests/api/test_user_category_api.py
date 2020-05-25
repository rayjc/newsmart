"""UserCategory API tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/api/test_user_category_api.py
#   python -m unittest discover tests/api/
# Note: This is necessary to avoid relative/absolute import based on path.

import os
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
from models import User, Category, UserCategory, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


class UserCategoryTagApiTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Category.query.delete()

        category1 = Category.new("test1")
        category2 = Category.new("test2")
        user = User.register(
            "test", "raw_password", "test@test.com",
            "Test", "User"
        )

        # keep track of id reference instead of db reference
        # db session may get refreshed after modifying session...
        self.category1_id = category1.id
        self.category2_id = category2.id
        self.user_id = user.id

    def tearDown(self):
        db.session.rollback()

    def test_create_article_tag(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id
            resp = client.put(
                "/api/usercategory",
                json={
                    "category_ids": [self.category1_id, self.category2_id]
                }
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.is_json)
        self.assertIn("users_categories", resp.get_json())
        self.assertListEqual(
            [self.category1_id, self.category2_id],
            [
                user_category['category_id']
                for user_category in resp.get_json()['users_categories']
            ]
        )

        with self.subTest('Missing category_ids'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.put(
                    "/api/usercategory",
                    json={}
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("category_ids", resp.get_json()['errors'])

        with self.subTest('Invalid category_ids'):
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.user_id
                resp = client.put(
                    "/api/usercategory",
                    json={
                        "category_ids": [str(self.category1_id), self.category2_id]
                    }
                )
            self.assertEqual(resp.status_code, 400)
            self.assertTrue(resp.is_json)
            self.assertIn("errors", resp.get_json())
            self.assertIn("category_ids", resp.get_json()['errors'])

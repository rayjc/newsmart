"""Tag model tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/test_tag_model.py
#   python -m unittest discover tests
# Note: This is necessary to avoid relative/absolute import based on path.

import os
import datetime
import logging
from unittest import TestCase

from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///newsmart-test"

# Now we can import app
from app import app
from models import Category, User, UserCategory, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


class ArticleModelTestCase(TestCase):

    def setUp(self):
        """Remove existing tables, create sample user"""

        Category.query.delete()
        User.query.delete()
        # intermediate tables should have been removed due to on delete cascade

        self.category = Category(name="Test")

        db.session.add(self.category)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_model(self):
        self.assertIs(self.category, Category.query.get(self.category.id))

        self.assertEqual(len(self.category.users_categories), 0)
        self.assertEqual(len(self.category.users), 0)

    def test_relationship_articles(self):
        user = User.register(
            "test", "raw_password", "test@test.com",
            "Test", "User"
        )
        user_category = UserCategory.new(user.id, self.category.id)

        with self.subTest():
            self.assertIn(user, self.category.users)

        with self.subTest():
            self.assertIn(user_category, self.category.users_categories)

    def test_news_method(self):
        category = Category.new("DC")

        self.assertIs(category, Category.query.get(category.id))

        # create request context for flash messages
        with app.test_request_context() as ctx:
            dup_category = Category.new("DC")
            self.assertIsNone(dup_category)

    def test_serialize_method(self):
        data = self.category.serialize()

        self.assertIsInstance(data, dict)
        self.assertDictEqual(
            data,
            {
                "id": self.category.id,
                "name": self.category.name,
            }
        )

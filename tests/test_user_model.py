"""User model tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/test_user_model.py
#   python -m unittest discover tests
# Note: This is necessary to avoid relative/absolute import based on path.

import os
from unittest import TestCase

from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///newsmart-test"

# Now we can import app
from app import app
from models import User, Saves, Article, Category, UserCategory, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True


class UserModelTestCase(TestCase):
    
    def setUp(self):
        """Remove existing tables, create sample user"""

        User.query.delete()
        Article.query.delete()
        Category.query.delete()
        # intermediate tables should have been removed due to on delete cascade

        # manually hashed the password since we are avoiding using register() here
        hashed = User.bcrypt.generate_password_hash("RAW_PASSWORD")
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        self.user1 = User(
            email="test1@test.com",
            username="testuser1",
            password=hashed_utf8,
            first_name="Test",
            last_name="User1"
        )
        
        db.session.add(self.user1)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_model(self):
        self.assertIsNotNone(
            User.query.filter(User.username == self.user1.username).one_or_none()
        )

        with self.subTest():
            self.assertEqual(len(self.user1.saves), 0)
            self.assertEqual(len(self.user1.articles), 0)

        with self.subTest():
            self.assertEqual(len(self.user1.users_categories), 0)
            self.assertEqual(len(self.user1.categories), 0)

    def test_relationship_articles(self):
        """Test articles and saves relationship (many-to-many)"""
        article = Article.new(
            "Test Article", "n/a", "http://www.google.com", "Google News",
        )
        saves = Saves.new(self.user1.id, article.id)

        with self.subTest():
            self.assertIn(article, self.user1.articles)
        
        with self.subTest():
            self.assertIn(saves, self.user1.saves)

    def test_relationship_categories(self):
        """Test categories and user_categories relationship (many-to-many)"""
        category = Category.new("General")
        user_category = UserCategory.new(self.user1.id, category.id)

        with self.subTest():
            self.assertIn(category, self.user1.categories)
        
        with self.subTest():
            self.assertIn(user_category, self.user1.users_categories)

    def test_register_method(self):
        user = User.register(
            "DarkKnight", "batman has no fear", "dk@wayne.com",
            "Bruce", "Wayne"
        )

        self.assertIs(user, User.query.get(user.id))
        self.assertNotEqual(user.password, "batman has no fear")

        with self.subTest("Duplicate username"):
            # create request context for flash messages
            with app.test_request_context() as ctx:
                dup_user = User.register(
                    "DarkKnight", "batman has no fear", "test@wayne.com",
                    "Bruce", "Wayne"
                )
                self.assertIsNone(dup_user)

        with self.subTest("Duplicate email"):
            # create request context for flash messages
            with app.test_request_context() as ctx:
                dup_user = User.register(
                    "Test", "batman has no fear", "dk@wayne.com",
                    "Bruce", "Wayne"
                )
                self.assertIsNone(dup_user)

    def test_update_method(self):
        old_username = self.user1.username
        user = User.update(old_username, "newtestuser", "RAW_PASSWORD")
        self.assertIsNone(
            User.query.filter(User.username == old_username).one_or_none()
        )
        self.assertIs(user, User.query.get(user.id))

        with self.subTest("Wrong password"):
            # create request context for flash messages
            with app.test_request_context() as ctx:
                invalid_user = User.update(user.username, "someuser", "WRONG_PASSWORD")
                self.assertIsNone(invalid_user)
        
        with self.subTest("Duplicate new username"):
            # create a new user to collide username
            batman = User.register(
                "DarkKnight", "batman has no fear", "dk@wayne.com",
                "Bruce", "Wayne"
            )
            # create request context for flash messages
            with app.test_request_context() as ctx:
                invalid_user = User.update(user.username, "DarkKnight", "WRONG_PASSWORD")
                self.assertIsNone(invalid_user)

    def test_authenticate_method(self):
        batman = User.register(
            "DarkKnight", "batman has no fear", "dk@wayne.com",
            "Bruce", "Wayne"
        )
        
        with self.subTest("Correct Password"):
            self.assertIs(
                batman, User.authenticate(batman.username, "batman has no fear")
            )

        with self.subTest("Incorrect Password"):
            self.assertIsNone(User.authenticate(batman.username, "WRONG_PASSWORD"))

    def test_full_name_property(self):
        self.assertEqual(self.user1.full_name, "Test User1")

"""User model tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/test_article_model.py
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
from models import User, Saves, Article, Tag, ArticleTag, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


class ArticleModelTestCase(TestCase):

    def setUp(self):
        """Remove existing tables, create sample user"""

        Article.query.delete()
        User.query.delete()
        Tag.query.delete()
        # intermediate tables should have been removed due to on delete cascade

        self.article = Article(
            title="Test Article",
            summary="Short summary",
            content="Some content",
            url="http://www.google.com",
            source="Google-News",
            img_url="https://source.unsplash.com/daily",
            timestamp=(datetime.datetime.today() - datetime.timedelta(days=2)),
        )

        db.session.add(self.article)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_model(self):
        self.assertIs(self.article, Article.query.get(self.article.id))
        
        with self.subTest():
            self.assertEqual(len(self.article.saves), 0)
            self.assertEqual(len(self.article.users), 0)
        
        with self.subTest():
            self.assertEqual(len(self.article.articles_tags), 0)
            self.assertEqual(len(self.article.tags), 0)

    def test_relationship_users(self):
        user = User.register(
            "test", "raw_password", "test@test.com",
            "Test", "User"
        )
        saves = Saves.new(user.id, self.article.id)

        with self.subTest():
            self.assertIn(user, self.article.users)

        with self.subTest():
            self.assertIn(saves, self.article.saves)

    def test_relationship_tags(self):
        tag = Tag.new("debug")
        article_tag = ArticleTag.new(self.article.id, tag.id)

        with self.subTest():
            self.assertIn(tag, self.article.tags)

        with self.subTest():
            self.assertIn(article_tag, self.article.articles_tags)

    def test_news_method(self):
        article = Article.new(
            "Secret", "Bruce Wayne is the Batman",
            "http://www.bing.com",
            "The Joker"
        )

        self.assertIs(article, Article.query.get(article.id))

        # create request context for flash messages
        with app.test_request_context() as ctx:
            dup_article = Article.new(
                "Disclosure", "Vigilante hunting crimimals",
                "http://www.bing.com",
                "The Joker"
            )
            self.assertIsNone(dup_article)

    def test_serialize_method(self):
        data = self.article.serialize()
        
        self.assertIsInstance(data, dict)
        self.assertDictEqual(
            data,
            {
                "id": self.article.id,
                "title": self.article.title,
                "summary": self.article.summary,
                "content": self.article.content,
                "url": self.article.url,
                "source": self.article.source,
                "img_url": self.article.img_url,
                "timestamp": self.article.timestamp.isoformat(),
            }
        )

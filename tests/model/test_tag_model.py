"""Tag model tests."""

# from newsmart/, run this test like:
#   python -m unittest tests/model/test_tag_model.py
#   python -m unittest discover tests/model/
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
from models import Article, Tag, ArticleTag, db

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.testing = True

logging.disable(logging.CRITICAL)   # Disable logging


class ArticleModelTestCase(TestCase):

    def setUp(self):
        """Remove existing tables, create sample user"""

        Tag.query.delete()
        Article.query.delete()
        # intermediate tables should have been removed due to on delete cascade

        self.tag = Tag(keyword="testing")

        db.session.add(self.tag)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()

    def test_model(self):
        self.assertIs(self.tag, Tag.query.get(self.tag.id))

        self.assertEqual(len(self.tag.articles_tags), 0)
        self.assertEqual(len(self.tag.articles), 0)

    def test_relationship_articles(self):
        article = Article.new(
            "Secret", "Bruce Wayne is the Batman",
            "http://www.bing.com",
            "The Joker"
        )
        article_tag = ArticleTag.new(article.id, self.tag.id)

        with self.subTest():
            self.assertIn(article, self.tag.articles)

        with self.subTest():
            self.assertIn(article_tag, self.tag.articles_tags)

    def test_news_method(self):
        tag = Tag.new("DC")

        self.assertIs(tag, Tag.query.get(tag.id))

        # create request context for flash messages
        with app.test_request_context() as ctx:
            dup_tag = Tag.new("DC")
            self.assertIsNone(dup_tag)

    def test_serialize_method(self):
        data = self.tag.serialize()

        self.assertIsInstance(data, dict)
        self.assertDictEqual(
            data,
            {
                "id": self.tag.id,
                "keyword": self.tag.keyword,
            }
        )

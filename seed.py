"""Seed file to make sample data for newsmart db."""
import datetime

from app import app
from models import (Article, ArticleTag, Category, Saves, Tag, User,
                    UserCategory, db, NEWS_CATEGORIES)

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
db.session.query(User).delete()
db.session.query(Article).delete()
db.session.query(Tag).delete()
db.session.query(Category).delete()

# user
users = [
    User.register("test1", "testing", "test1@test.com", "Test1", "User"),
    User.register("test2", "testing", "test2@test.com", "Test2", "User"),
]

# articles
articles = [
    Article.new("Google", "n/a", "http://www.google.com", "Google"),
    Article.new(
        "Elon Musk restarts Tesla factory in California in violation of lockdown order",
        """Tesla CEO Elon Musk confirmed on Twitter Monday that the company 
        has restarted its California factory in violation of local government orders...""",
        "https://www.cbc.ca/news/world/musk-reopens-tesla-factory-1.5565269",
        "CBC", summary="...",
        img_url="https://i.cbc.ca/1.5565297.1589234487!/cpImage/httpImage/image.jpg_gen/derivatives/16x9_780/virus-outbreak-tesla.jpg",
        timestamp=(datetime.datetime.today() - datetime.timedelta(days=10))),
    Article.new(
        "Shanghai Disneyland reopens with anti-virus controls - The Associated Press",
        """SHANGHAI (AP) Visitors in face masks streamed into Shanghai Disneyland as the 
        theme park reopened Monday in a high-profile step toward reviving global tourism 
        that was shut down by the coronavirus pandemic. \r\nThe House of Mouses 
        experience in Shanghai, the fi… [+3508 chars]""",
        "https://apnews.com/23f592c0edfb1d27df98cb5a6e7674f9",
        "Associated Press",
        """SHANGHAI (AP) — Visitors in face masks streamed into Shanghai Disneyland 
        as the theme park reopened Monday in a high-profile step toward 
        reviving global tourism that was shut down by the...""",
        "https://storage.googleapis.com/afs-prod/media/25c249e4cbf64b71ab79a8b1b83d5d20/3000.jpeg"
    )
]

# tags
tags = [
    Tag.new("gold"),
    Tag.new("Technology"), Tag.new("Tesla"), Tag.new("pandemic"), Tag.new("lockdown"),
    Tag.new("Disney")
]

# categories
categories = [Category.new(name) for name in NEWS_CATEGORIES]

saves = [
    Saves.new(users[0].id, articles[0].id),
    Saves.new(users[0].id, articles[1].id),
    Saves.new(users[0].id, articles[2].id),
    Saves.new(users[1].id, articles[2].id),
]

article_tags = [
    ArticleTag.new(articles[0].id, tags[0].id),
    ArticleTag.new(articles[1].id, tags[1].id),
    ArticleTag.new(articles[1].id, tags[2].id),
    ArticleTag.new(articles[1].id, tags[3].id),
    ArticleTag.new(articles[1].id, tags[4].id),
    ArticleTag.new(articles[2].id, tags[3].id),
    ArticleTag.new(articles[2].id, tags[4].id),
    ArticleTag.new(articles[2].id, tags[5].id)
]

user_categories = [
    UserCategory.new(users[0].id, categories[0].id),
    UserCategory.new(users[0].id, categories[2].id),
    UserCategory.new(users[0].id, categories[4].id),
    UserCategory.new(users[1].id, categories[1].id),
    UserCategory.new(users[1].id, categories[3].id),
    UserCategory.new(users[1].id, categories[5].id),
]

# Add new objects to session, so they'll persist
db.session.add_all(users)
db.session.add_all(articles)
db.session.add_all(tags)
db.session.add_all(categories)
db.session.add_all(saves)
db.session.add_all(article_tags)
db.session.add_all(user_categories)

# Commit--otherwise, this never gets saved!
db.session.commit()

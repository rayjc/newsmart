from flask import g

from models import Saves
from news_api_session import NewsApiSession
from nlu_api_session import NLUApiSession


class NewSmart(NewsApiSession, NLUApiSession):
    
    def get_user_category_articles(self, limit=10):
        """
        Return a dictionary of category name as key and list of article objects as value
        from categories that user has saved.
        """
        category_map = dict()
        if g.user:
            category_map = {
                category.name: self.get_top_articles(
                    category=category.name, size=limit)
                for category in g.user.categories
            }
        return category_map

    def get_recommended_articles(self):
        """
        Return a list of articles recommended based on user's bookmarks.
        """
        related_articles = []
        if g.user:
            # 5 most recent articles saved by user
            saves = (
                Saves.query.filter(Saves.user_id == g.user.id)
                        .order_by(Saves.timestamp.desc())
                        .limit(5).all()
            )
            for save in saves:
                # extract tags
                tags = [tag.keyword for tag in save.article.tags]
                # compose a phrase from concepts then keywords
                phrase = " ".join(tags[::-1])
                # search articles based on phrase
                articles = self.search_articles(phrase, size=3,
                                                exclude_domains=NewSmart.video_urls)
                related_articles.extend(articles)
        return related_articles


    def get_bookmarked_urls(self):
        """Return a set of article urls that user has bookmarked"""
        bookmarked_urls = (
            {article.url for article in g.user.articles}
            if g.user else
            {}
        )
        return bookmarked_urls

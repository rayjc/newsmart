from flask import g

from models import Saves
from news_api_session import NewsApiSession
from nlu_api_session import NLUApiSession


class NewSmart(NewsApiSession, NLUApiSession):
    max_terms = 4
    
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
            # 4 most recent articles saved by user
            saves = (
                Saves.query.filter(Saves.user_id == g.user.id)
                        .order_by(Saves.timestamp.desc())
                        .limit(4).all()
            )
            batch_size = 3 if len(saves) > 2 else 4
            for save in saves:
                # extract tags
                tags = [tag.keyword for tag in save.article.tags]
                if len(tags) > NewSmart.max_terms:
                    # truncate words
                    tags = tags[:NewSmart.max_terms]
                # compose a phrase; tags include concepts followed by keywords
                phrase = " ".join(tags)
                # search articles based on phrase
                articles = self.search_articles(phrase, size=batch_size,
                                                exclude_domains=NewSmart.video_urls) or []
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
    
    def get_bookmark_url_to_id(self):
        """
        Return a map of bookmarked article url to bookmark id.
        """
        bookmark_map = (
            {saves.article.url: saves.id for saves in g.user.saves}
            if g.user else
            {}
        )
        return bookmark_map

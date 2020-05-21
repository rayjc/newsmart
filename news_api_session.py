import os
import datetime

from base_api_session import BaseApiSession


class NewsApiSession(BaseApiSession):
    news_key = os.environ["NEWS_API_KEY"]    # raise exception if not set
    headlines_url = "https://newsapi.org/v2/top-headlines"
    articles_url = "https://newsapi.org/v2/everything"

    def get_top_articles(self, country='us', category=None, size=None):
        """
        Send API request to newsapi.org;
        return a list of article objects.
        Note: No query search for this url since results are limited.
        article = {
            "source": {
                "id",
                "name"
            },
            "author",
            "title",
            "description",
            "url",
            "urlToImage",
            "publishedAt": "2020-05-11T21:15:18Z",
            "content",
        }
        """
        params = {"apiKey": NewsApiSession.news_key, "country": country}
        if category:
            params.update({"category": category})
        if size:
            params.update({"pageSize": size})
        
        resp = self.get(NewsApiSession.headlines_url, params)

        return resp.get("articles") if resp else resp

    def search_articles(self, phrase, size=None, sort="popularity",
                        language="en", days=7, exclude_domains=[]):
        """
        Search for articles for specified phrase;
        return a list of article objects.
        """
        assert sort in ("publishedAt", "relevancy", "popularity")
        params = {
            "apiKey": NewsApiSession.news_key, "language": language,
            "q": phrase, "sortBy": sort,
        }
        if sort == "popularity":
            # limit search to recent two weeks
            from_date = datetime.datetime.today() - datetime.timedelta(days=days)
            params.update({"from": from_date.isoformat()})
        if size:
            params.update({"pageSize": size})
        if exclude_domains:
            params.update({"excludeDomains" : ",".join(exclude_domains)})
        
        resp = self.get(NewsApiSession.articles_url, params)

        return resp.get("articles") if resp else resp

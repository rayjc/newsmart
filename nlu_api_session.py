import os

from base_api_session import BaseApiSession


class NLUApiSession(BaseApiSession):
    nlu_key = os.environ["NLU_API_KEY"]    # raise exception if not set
    analytics_url = f"{os.environ['NLU_URL']}/v1/analyze?version=2019-07-12"
    # Need a way to avoid using NLP on non-textual webpages...
    # For now, youtube.com seems to be the only source of video news in NewsAPI
    video_urls = {"youtube.com"}

    def analyze_url(self, url, limit=10):
        """
        Request IBM Watson NLU instance to extract sentiment, keywords, concepts
        for specified url; return lists of sentiment, keyword, concept objects.
        """
        json = {
            "url": url,
            "features": {
                "sentiment": {},
                "concepts": {
                    "limit": limit
                },
                "keywords": {
                    "limit": limit,
                    "sentiment": True
                }
            }
        }
        resp = self.post(NLUApiSession.analytics_url,
                        json, auth=('apiKey', NLUApiSession.nlu_key))
        
        return resp
    
    def get_relevant_terms(self, url, limit=5,
                           keyword_relevance=0.7, concept_relevance=0.9):
        """
        Request and extract keywords and concepts for specified url;
        return an object consists of keywords and concepts filtered
        based on relevance.
        Note: keywords indicate more specific events or mentioning;
        concepts indicate more generic terms or categories.
        return_object = {
            "keywords": [],
            "concepts": []
        }
        """
        resp = (
            None
            # do not use NLP on video urls
            if any(video_url in url for video_url in NLUApiSession.video_urls) else
            self.analyze_url(url, limit)
        )

        if not resp:
            return {"keywords": [], "concepts": []}

        keywords = [
            keyword['text']
            for keyword in resp['keywords']
            if keyword['relevance'] > keyword_relevance
        ]
        concepts = [
            concept['text']
            for concept in resp['concepts']
            if concept['relevance'] > concept_relevance
        ]

        return {"keywords": keywords, "concepts": concepts}

import os

from base_api_session import BaseApiSession


class NLUApiSession(BaseApiSession):
    nlu_key = os.environ["NLU_API_KEY"]    # raise exception if not set
    analytics_url = f"{os.environ['NLU_URL']}/v1/analyze?version=2019-07-12"

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
        resp = self.analyze_url(url, limit)

        if not resp:
            {"keywords": [], "concepts": []}

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

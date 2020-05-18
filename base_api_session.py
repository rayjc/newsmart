import os
import urllib

import requests

from logger import logger

MAX_TIMEOUT = 10

class BaseApiSession:
    
    def get(self, url, params):
        """
        Wrap requests.get() with error handling;
        return response in JSON.
        """
        # encode and escape url manually
        # this is needed for space characters
        # requests.get() converts space to + instead of %20
        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        try:
            resp = requests.get(url, params, timeout=MAX_TIMEOUT)
        except requests.Timeout:
            logger.critical(f"GET request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"Response: {e.response}\nRequest: {e.request}")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None

        return resp.json()
    
    def post(self, url, json):
        """
        Wrap requests.post() with error handling;
        return response in JSON.
        """
        try:
            resp = requests.post(url, json, timeout=MAX_TIMEOUT)
        except requests.Timeout:
            logger.critical(f"POST request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"Response: {e.response}\nRequest: {e.request}")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None

        return resp.json()
    
    def delete(self, url):
        """
        Wrap requests.deletes() with error handling;
        return response in JSON.
        """
        try:
            resp = requests.delete(url, timeout=MAX_TIMEOUT)
        except requests.Timeout:
            logger.critical(f"DELETE request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"Response: {e.response}\nRequest: {e.request}")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None

        return resp.json()

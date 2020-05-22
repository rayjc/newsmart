import os
import urllib

import requests

from logger import logger

MAX_TIMEOUT = 10

class BaseApiSession:
    
    def get(self, url, params, timeout=MAX_TIMEOUT, **kwargs):
        """
        Wrap requests.get() with error handling;
        return response in JSON.
        """
        # encode and escape url manually
        # this is needed for space characters
        # requests.get() converts space to + instead of %20
        params = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        try:
            resp = requests.get(url, params, timeout=timeout, **kwargs)
            resp.raise_for_status()
        except requests.Timeout:
            logger.critical(f"GET request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"GET request: {e} - body: {e.request.body.decode()}")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None

        return resp.json()
    
    def post(self, url, data, timeout=MAX_TIMEOUT, ** kwargs):
        """
        Wrap requests.post() with error handling;
        return response in JSON.
        """
        try:
            resp = requests.post(url, json=data, timeout=timeout, **kwargs)
            resp.raise_for_status()
        except requests.Timeout:
            logger.critical(f"POST request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"POST request: {e} - body: {e.request.body.decode()}")
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
            resp.raise_for_status()
        except requests.Timeout:
            logger.critical(f"DELETE request timed out!")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None
        except requests.RequestException as e:
            logger.error(f"DELETE request: {e} - body: {e.request.body.decode()}")
            if os.environ.get("FLASK_ENV") == "development":
                raise
            return None

        return resp.json()

    def isUrlValid(self, url, timeout=0.5, **kwargs):
        """
        Check if url is valid only (not if it is alive);
        return True if it is; otherwise False.
        """
        try:
            resp = requests.head(url, timeout=timeout,
                                 **kwargs).raise_for_status()
        except requests.Timeout:
            logger.warning(f"HEAD request timed out for {url}")
            return True
        except requests.HTTPError as e:
            logger.warning(f"HEAD request: {e}")
            return True
        except requests.RequestException as e:
            logger.error(f"ERROR: {e}")
            return False

        return True

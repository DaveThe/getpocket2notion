
# import json
# from datetime import datetime

# import pytz
import requests

from utility.logs import setup_log

logger = setup_log(module_name=__name__, log_level="DEBUG")


class Pocket():
    def __init__(self, consumer_key, user_email, password, browser):
        """Getpocket handler

        Args:
            consumer_key (string): getpocket apikey
            user_email (string): getpocket user mail
            password (string): getpocket password
            browser (string): Browser settings
        """
        self.browser = browser
        self.user_email = user_email
        self.password = password
        self.consumer_key = consumer_key
        self.request_token = ''
        self.access_token = ''
        self.items = {}

    def get_request_token(self, redirect_uri='http://www.google.com'):

        auth_data = {
            'consumer_key': self.consumer_key,
            'redirect_uri': redirect_uri
        }
        headers = {'Content-type': 'application/json; charset=UTF8', 'X-Accept': 'application/json'}
        request_token = requests.post('https://getpocket.com/v3/oauth/request', json=auth_data, headers=headers)

        response_token = request_token.json()
        logger.debug(response_token)

        self.browser.get(
            f"https://getpocket.com/auth/authorize?request_token={response_token['code']}&redirect_uri={redirect_uri}")

        username = self.browser.find_element_by_id("feed_id")
        username.clear()
        username.send_keys(self.user_email)

        password = self.browser.find_element_by_id("login_password")
        password.clear()
        password.send_keys(self.password)

        self.browser.find_elements_by_class_name("btn-authorize")[0].click()

        self.browser.quit()

        self.request_token = response_token['code']

    def get_access_token(self):

        authorize_data = {
            "consumer_key": self.consumer_key,
            "code": self.request_token
        }
        headers = {'Content-type': 'application/json; charset=UTF8', 'X-Accept': 'application/json'}

        request_access_token = requests.post('https://getpocket.com/v3/oauth/authorize',
                                             json=authorize_data, headers=headers)

        if request_access_token:
            response_access_token = request_access_token.json()
            logger.debug(response_access_token)
            self.access_token = response_access_token['access_token']
        else:
            error_code = request_access_token.headers['x-error-code']
            error = request_access_token.headers['x-error']
            logger.error(f"Error code: {error_code} - {error}")

    def authenticate(self):
        if not self.request_token or not self.access_token:
            logger.debug("mi riautentico")
            if not self.request_token:
                self.get_request_token()
            if not self.access_token:
                self.get_access_token()

    def get_items(self, count=10, detailType='complete', state='unread'):
        self.authenticate()

        data = {
            "consumer_key": self.consumer_key,
            "access_token": self.access_token,
            "count": count,
            "detailType": detailType,
            "state": state
        }
        headers = {'Content-type': 'application/json; charset=UTF8', 'X-Accept': 'application/json'}

        request_items = requests.post('https://getpocket.com/v3/get',
                                      json=data,
                                      headers=headers)

        if request_items:
            items = request_items.json()
            # logger.debug(response_access_token)
            self.items = items
            return self.items
        else:
            error_code = request_items.headers['x-error-code']
            error = request_items.headers['x-error']
            logger.error(f"Error code: {error_code} - {error}")
            self.items = {}
            return self.items

    def set_items_archive(self, item_ids):
        self.authenticate()

        # server_timezone = pytz.timezone("Europe/Rome")
        # server_time = datetime.now(server_timezone)
        item_data = []
        for item_id in item_ids:
            item_data.append(
                {
                    "action": "archive",
                    "item_id": item_id
                }
            ),
            # "time": server_time  # "1348853312"

        data = {
            "consumer_key": self.consumer_key,
            "access_token": self.access_token,
            "actions": item_data
        }
        headers = {'Content-type': 'application/json; charset=UTF8', 'X-Accept': 'application/json'}
        set_to_archive = requests.post('https://getpocket.com/v3/send',
                                       json=data,
                                       headers=headers)

        if set_to_archive:
            response_archive = set_to_archive.json()
            # logger.debug(response_access_token)
            return response_archive
        else:
            error_code = set_to_archive.headers['x-error-code']
            error = set_to_archive.headers['x-error']
            logger.error(f"Error code: {error_code} - {error}")
            return False

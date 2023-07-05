import os
from django.apps import AppConfig

CLIENT_ID = "d9020c4acb2d4a51aa18e83c3d632dbe"
CLIENT_SECRET = "QNVjvp5yWf7ayc00qbS7Cv674549zR3IVV1lUi7aKgdZunUJS0vHxfvzgipa5jXX"
ACCESS_TOKEN = ""

PREFIX_URL = "https://allegro.pl.allegrosandbox.pl"
# PREFIX_URL = "https://allegro.pl"
TOKEN_URL = PREFIX_URL + "/auth/oauth/token"


class AllegrotrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AllegroTracker'

    # def ready(self):
    #     if os.environ.get('RUN_MAIN'):
    #         import requests
    #         import json
    #         global ACCESS_TOKEN
    #         try:
    #             data = {'grant_type': 'client_credentials'}
    #             access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
    #                                                   allow_redirects=False, auth=(CLIENT_ID, CLIENT_SECRET))
    #             tokens = json.loads(access_token_response.text)
    #             ACCESS_TOKEN = tokens['access_token']
    #             print("access token = " + ACCESS_TOKEN)
    #         except requests.exceptions.HTTPError as err:
    #             raise SystemExit(err)

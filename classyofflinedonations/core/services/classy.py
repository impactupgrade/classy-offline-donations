import os
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session


def get_access_token():
    client = BackendApplicationClient(os.environ['CLASSY_CLIENT_ID'])
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://api.classy.org/oauth2/auth', client_id=os.environ['CLASSY_CLIENT_ID'],
        client_secret=os.environ['CLASSY_CLIENT_SECRET'])
    print(token)
    return token


def get_json(path):
    token = get_access_token()
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.get("https://api.classy.org/2.0/" + path)
    return resp.json()


def has_account(email):
    json = get_json("members/" + email)
    return "error" not in json


# >>> from requests_oauthlib import OAuth2Session
# >>> from oauthlib.oauth2 import TokenExpiredError
# >>> try:
# ...     client = OAuth2Session(client_id, token=token)
# ...     r = client.get(protected_url)
# >>> except TokenExpiredError as e:
# ...     token = client.refresh_token(refresh_url, **extra)
# ...     token_saver(token)
# >>> client = OAuth2Session(client_id, token=token)
# >>> r = client.get(protected_url)

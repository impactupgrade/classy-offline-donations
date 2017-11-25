import os
from oauthlib.oauth2 import LegacyApplicationClient, BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json


# def set_access_token(username, password, session):
#     client = LegacyApplicationClient(client_id=os.environ['CLASSY_CLIENT_ID'])
#     oauth = OAuth2Session(client=client)
#     token = oauth.fetch_token(token_url='https://api.classy.org/oauth2/auth', client_id=os.environ['CLASSY_CLIENT_ID'],
#         client_secret=os.environ['CLASSY_CLIENT_SECRET'], username=username, password=password)
#     session['CLASSY_TOKEN'] = token


def get_access_token():
    client = BackendApplicationClient(client_id=os.environ['CLASSY_CLIENT_ID'])
    oauth = OAuth2Session(client=client)
    return oauth.fetch_token(token_url='https://api.classy.org/oauth2/auth', client_id=os.environ['CLASSY_CLIENT_ID'],
                             client_secret=os.environ['CLASSY_CLIENT_SECRET'])


def set_access_token(email, session):
    session['CLASSY_TOKEN'] = get_access_token()
    session['CLASSY_MEMBER_ID'] = get_member_id(email)


def get_json(path, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.get("https://api.classy.org/2.0/" + path)
    json_data = resp.json()
    print(json_data)
    return json_data


def post_json(path, json_data, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.post("https://api.classy.org/2.0/" + path, json=json_data)
    return resp.json()


def get_member_id(email):
    # TODO: Need to verify the correct CLASSY_ORG_ID as well with /members/{id}/organizations
    json_data = get_json("members/" + email, get_access_token())
    return str(json_data['id'])


def has_account(email):
    # TODO: Need to verify the correct CLASSY_ORG_ID as well with /members/{id}/organizations
    json_data = get_json("members/" + email, get_access_token())
    return "error" not in json_data


def get_fundraisers(session):
    fundraisers = {}

    json_data = get_json("/members/" + session['CLASSY_MEMBER_ID'] + "/fundraising-pages?with=fundraising_team,campaign",
                         session['CLASSY_TOKEN'])
    # TODO (and not sure if the with=campaign is even valid)
    # for fundraiserJson in json_data['data']:
    #     campaigns[campaignJson['id']] = campaignJson['name']
    print(json_data)

    return fundraisers


def create_donation(donation_form, session):
    page_id = donation_form.cleaned_data['fundraisers']  # TODO: 'fundraisers' is a ChoiceField -- is this correct?
    campaign_id = "1234"  # TODO Get from API using the fundraiser page id

    donation = {}
    # {
    #     "billing_address1": "533 F Street",
    #     "billing_city": "San Diego",
    #     "billing_country": "US",
    #     "billing_first_name": "Classy",
    #     "billing_last_name": "Member",
    #     "billing_postal_code": "92101",
    #     "billing_state: `CA` (string, optional) - Billing state/province. Required if billing_country is US": "Hello, world!",
    #     "comment": "This is a comment",
    #     "company_name": "Company",
    #     "fundraising_page_id": 222,
    #     "fundraising_team_id": 333,
    #     "is_anonymous": false,
    #     "items": [
    #         {
    #             "price": 55,
    #             "overhead_amount": 25,
    #             "product_id": 123,
    #             "product_name": "Offline Donation",
    #             "quantity": 2,
    #             "type": "donation"
    #         }
    #     ],
    #     "member_email_address": "member@classy.org",
    #     "member_name": "Classy Member",
    #     "member_phone": "555-555-5555",
    #     "offline_payment_info": {
    #         "check_number": "123456",
    #         "description": "Transaction Item Description",
    #         "payment_type": "cash",
    #     },
    # }
    json_data = json.dumps(donation)

    post_json("/campaigns/" + campaign_id + "/transactions", json_data, session['CLASSY_TOKEN'])


# os.environ['CLASSY_CLIENT_ID'] = "QKf0bWUA1exCDy79"
# os.environ['CLASSY_CLIENT_SECRET'] = "T8A4aDx1rZ8SG5yK"
# __session = {}
# set_access_token( __session)
# json_data = get_json("/members/" + str(5922949), __session)
# # json_data = get_json("/members/" + str(5922949) + "/fundraising-pages?with=fundraising_team,campaign", __session)
# print(json_data)

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

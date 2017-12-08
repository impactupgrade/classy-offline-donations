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
    # TODO: Set timeout rather high...
    return oauth.fetch_token(token_url='https://api.classy.org/oauth2/auth', client_id=os.environ['CLASSY_CLIENT_ID'],
                             client_secret=os.environ['CLASSY_CLIENT_SECRET'])


def set_access_token(email, session):
    session['CLASSY_MEMBER_ID'] = get_member_id(email)
    session['CLASSY_TOKEN'] = get_access_token()


def get_json(path, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.get("https://api.classy.org/2.0/" + path)
    json_data = resp.json()
    return json_data


def post_json(path, json_data, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.post("https://api.classy.org/2.0/" + path, json=json_data)
    return resp.json()


def get_member_id(email):
    json_data = get_json("members/" + email, get_access_token())
    return str(json_data['id'])


def has_account(email):
    json_data = get_json("members/" + email, get_access_token())
    return "error" not in json_data


def get_fundraisers(session):
    fundraisers = {}

    json_data = get_json("/organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id="
                         + session['CLASSY_MEMBER_ID'] + "&with=fundraising_team", get_access_token())
    # json_data = get_json("/organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id=5922949"
    #                      "&with=fundraising_team", get_access_token())
    for fundraiser_json in json_data['data']:
        fundraiser_label = fundraiser_json['title']
        if fundraiser_json['fundraising_team_id'] is not None:
            fundraiser_label += " (" + fundraiser_json['fundraising_team']['name'] + ")"
        fundraisers[fundraiser_json['id']] = fundraiser_label

    return fundraisers.items()


# TODO: Should likely only be applicable to team *leads* -- on hold
# def get_teams(session):
#     teams = {}
#
#
#
#     return teams


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
# os.environ['CLASSY_ORG_ID'] = "21729"
# __session = {}
# set_access_token("brett@3riverdev.com", __session)
# __json_data = get_json("/organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id=5922949&with=fundraising_team", get_access_token())
# {'total': 1, 'per_page': 20, 'current_page': 1, 'last_page': 1, 'next_page_url': None, 'prev_page_url': None, 'from': 1, 'to': 1, 'data': [{'status': 'active', 'fundraising_team_id': 143213, 'campaign_id': 145704, 'team_role': None, 'logo_id': 251766, 'cover_photo_id': None, 'commitment': None, 'thank_you_text': None, 'updated_at': '2017-11-15T13:39:16+0000', 'raw_currency_code': 'USD', 'raw_goal': '100.000', 'id': 1182331, 'member_id': 5922949, 'organization_id': 21729, 'designation_id': None, 'title': 'Faith Lewis', 'intro_text': '<p>Help us raise money for Destiny Rescue</p>', 'thankyou_email_text': None, 'member_email_text': None, 'logo_url': 'https://assets.classy.org/3543993/6f6a32fc-dd9a-11e6-9863-06028f6061f3.jpg', 'goal': '100.00', 'created_at': '2017-11-02T16:16:05+0000', 'started_at': '2017-11-02T04:00:00+0000', 'ended_at': None, 'alias': 'Faith Lewis', 'currency_code': 'USD', 'canonical_url': 'https://www.classy.org/fundraiser/1182331', 'fundraising_team': {'raw_currency_code': 'USD', 'id': 143213, 'name': 'DeKalb High School Bible Study', 'description': '<p>Help us raise money for Destiny Rescue</p>', 'goal': '300.00'}}]}
# __json_data = get_json("/organizations/" + os.environ['CLASSY_ORG_ID'] + "/supporters?filter=member_id=5922949", get_access_token())
# json_data = get_json("/members/" + str(5922949) + "/fundraising-pages?with=fundraising_team,campaign", get_access_token())
# print(__json_data)

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

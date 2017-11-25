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


def get_fundraiser(id):
    return get_json("/fundraising-pages/" + id, get_access_token())


# TODO: Should likely only be applicable to team *leads* -- on hold
# def get_teams(session):
#     teams = {}
#
#
#
#     return teams


def create_donation(donation_form, session):
    page_id = donation_form.cleaned_data['fundraisers']  # TODO: 'fundraisers' is a ChoiceField -- is this correct?
    # TODO: May eventually support donations for whole teams, and would need 'fundraising_team_id' set
    # TODO: Haven't tested get_fundraiser() yet...
    campaign_id = get_fundraiser(page_id)['campaign_id']

    first_name = donation_form.cleaned_data['first_name']
    last_name = donation_form.cleaned_data['last_name']

    company_name = donation_form.cleaned_data['company_name']

    # TODO: Unclear if these are needed.  Not sure if the `member_*` means they have to match actual Classy accounts.
    # email = donation_form.cleaned_data['email']
    # phone = donation_form.cleaned_data['phone']

    address = donation_form.cleaned_data['address']
    city = donation_form.cleaned_data['city']
    state = donation_form.cleaned_data['state']
    zip = donation_form.cleaned_data['zip']

    anonymous = donation_form.cleaned_data['anonymous']
    comment = donation_form.cleaned_data['comment']
    amount = donation_form.cleaned_data['amount']
    type = donation_form.cleaned_data['type']
    check_num = donation_form.cleaned_data['check_num']

    donation = {
        "billing_address1": address,
        "billing_city": city,
        "billing_country": "US",
        "billing_first_name": first_name,
        "billing_last_name": last_name,
        "billing_postal_code": zip,
        "billing_state": state,
        "comment": comment,
        "company_name": company_name,
        "fundraising_page_id": page_id,
        # "fundraising_team_id": 333,
        "is_anonymous": anonymous,
        "items": [
            {
                # TODO: In dollars?  Or cents?
                "price": amount,
                # TODO: Needed?
                # "overhead_amount": 25,
                # TODO: Needed?
                # "product_id": 123,
                "product_name": "Offline Donation",
                # TODO: Needed?
                # "quantity": 1,
                "type": type
            }
        ],
        # "member_email_address": "member@classy.org",
        # "member_name": "Classy Member",
        # "member_phone": "555-555-5555",
        "offline_payment_info": {
            "check_number": check_num,
            # TODO: Needed?
            # "description": "Transaction Item Description",
            "payment_type": "cash",
        },
        "metadata": {
            "approved": False
        },
    }
    json_data = json.dumps(donation)

    post_json("/campaigns/" + campaign_id + "/transactions", json_data, session['CLASSY_TOKEN'])


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

import os
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import json


def get_access_token(session):
    if 'CLASSY_TOKEN' in session:
        # TODO: Check if expired and support refresh (see commented-out code below)
        return session['CLASSY_TOKEN']
    else:
        client = BackendApplicationClient(client_id=os.environ['CLASSY_CLIENT_ID'])
        oauth = OAuth2Session(client=client)
        # TODO: Set timeout rather high...
        return oauth.fetch_token(token_url='https://api.classy.org/oauth2/auth', client_id=os.environ['CLASSY_CLIENT_ID'],
                                 client_secret=os.environ['CLASSY_CLIENT_SECRET'])


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


def set_access_token(email, session):
    session['CLASSY_MEMBER_ID'] = get_member_id(email, session)
    session['CLASSY_TOKEN'] = get_access_token(session)


def get_json(path, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.get("https://api.classy.org/2.0/" + path)
    json_data = resp.json()
    return json_data


def post_json(path, json_data, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.post("https://api.classy.org/2.0/" + path, json=json_data, headers={'Content-Type': 'application/json'})
    print(json_data)
    print("https://api.classy.org/2.0/" + path)
    print(resp.text)
    return resp.json()


def put_json(path, json_data, token):
    client = OAuth2Session(os.environ['CLASSY_CLIENT_ID'], token=token)
    resp = client.put("https://api.classy.org/2.0/" + path, json=json_data, headers={'Content-Type': 'application/json'})
    print(json_data)
    print("https://api.classy.org/2.0/" + path)
    print(resp.text)
    return resp.json()


def get_member_id(email, session):
    json_data = get_json("members/" + email, get_access_token(session))
    return str(json_data['id'])


def has_account(email, session):
    json_data = get_json("members/" + email, get_access_token(session))
    return "error" not in json_data


def get_fundraisers(session):
    fundraisers = {}

    json_data = get_json("organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id="
                         + session['CLASSY_MEMBER_ID'] + "&with=fundraising_team", get_access_token(session))
    for fundraiser_json in json_data['data']:
        fundraiser_label = fundraiser_json['title']
        if fundraiser_json['fundraising_team_id'] is not None:
            fundraiser_label += " (" + fundraiser_json['fundraising_team']['name'] + ")"
        fundraisers[fundraiser_json['id']] = fundraiser_label

    return fundraisers.items()


def get_fundraiser(id, session):
    return get_json("fundraising-pages/" + str(id), get_access_token(session))


# TODO: Should likely only be applicable to team *leads* -- on hold
# def get_teams(session):
#     teams = {}
#
#
#
#     return teams


def create_donation(donation_form, session):
    page_id = int(donation_form.cleaned_data['fundraiser'])  # TODO: Can a ChoiceField be typed and return an int value?
    # TODO: May eventually support donations for whole teams, and would need 'fundraising_team_id' set
    campaign_id = int(get_fundraiser(page_id, session)['campaign_id'])

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

    # TODO: Not working -- giving 'true' even when the first option is selected
    anonymous = bool(donation_form.cleaned_data['anonymous'])  # TODO: Use a BoolField with a Select widget?
    comment = donation_form.cleaned_data['comment']
    amount = float(donation_form.cleaned_data['amount'])  # float needed for JSON
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
                "price": amount,
                "product_name": "Offline Donation",
                "type": "donation"
            }
        ],
        # "member_email_address": "member@classy.org",
        # "member_name": "Classy Member",
        # "member_phone": "555-555-5555",
        "offline_payment_info": {
            "check_number": check_num,
            "payment_type": type,
        },
        # "metadata": {
        #     "approved": "false"
        # },
    }
    json_data = json.dumps(donation)
    # print(json_data)

    create_response = post_json("campaigns/" + str(campaign_id) + "/transactions", json_data, get_access_token(session))

    # update = {
    #     "status": "incomplete"
    # }
    # print("transactions/" + create_response['id'])
    # print(json.dumps(update))
    # put_json("transactions/" + create_response['id'], json.dumps(update), get_access_token(session))


def get_donations(session):
    # update = {
    #      "status": "incomplete"
    # }
    # put_json("transactions/9930815", json.dumps(update), get_access_token(session))

    # TODO: Limit only to needed fields.  Ex: &fields=id,billing_first_name,billing_last_name
    json_data = get_json("organizations/" + os.environ['CLASSY_ORG_ID'] + "/transactions?"
                                          + "filter=payment_method%3Doffline",
                         get_access_token(session))

    return json_data['data']

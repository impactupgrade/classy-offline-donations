import os
import requests
import time


def get_access_token(session):
    if 'CLASSY_TOKEN' not in session or 'CLASSY_TOKEN_EXP_TS' not in session\
            or time.time() >= session['CLASSY_TOKEN_EXP_TS']:
        set_access_token(session)

    return session['CLASSY_TOKEN']


def set_access_token(session):
    data = {'grant_type': 'client_credentials',
            'client_id': os.environ['CLASSY_CLIENT_ID'],
            'client_secret': os.environ['CLASSY_CLIENT_SECRET']}
    response = requests.post('https://api.classy.org/oauth2/auth', data=data)
    # print('https://api.classy.org/oauth2/auth')
    # print(response.text)
    json_data = response.json()
    session['CLASSY_TOKEN'] = json_data['access_token']
    session['CLASSY_TOKEN_EXP_TS'] = time.time() + json_data['expires_in']


def login(email, session):
    session['CLASSY_MEMBER_ID'] = get_member_id(email, session)
    set_access_token(session)


def get_json(path, session):
    token = get_access_token(session)
    headers = {'Authorization': 'BEARER ' + token}
    response = requests.get('https://api.classy.org/2.0/' + path, headers=headers)
    # print("https://api.classy.org/2.0/" + path)
    # print(response.text)
    return response.json()


def post_json(path, json_data, session):
    token = get_access_token(session)
    headers = {'Authorization': 'BEARER ' + token, 'Content-Type': 'application/json'}
    response = requests.post('https://api.classy.org/2.0/' + path, json=json_data, headers=headers)
    # print("https://api.classy.org/2.0/" + path)
    # print(json_data)
    # print(response.text)


def put_json(path, json_data, session):
    token = get_access_token(session)
    headers = {'Authorization': 'BEARER ' + token, 'Content-Type': 'application/json'}
    response = requests.put('https://api.classy.org/2.0/' + path, json=json_data, headers=headers)
    # print("https://api.classy.org/2.0/" + path)
    # print(json_data)
    # print(response.text)


def get_member_id(email, session):
    json_data = get_json("members/" + email, session)
    if 'id' in json_data:
        return str(json_data['id'])
    else:
        return None


def has_account(email, session):
    json_data = get_json("members/" + email, session)
    return 'error' not in json_data


def get_fundraisers(session):
    fundraisers = {}

    json_data = get_json("organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id="
                         + session['CLASSY_MEMBER_ID'] + "&with=fundraising_team", session)
    for fundraiser_json in json_data['data']:
        fundraiser_label = fundraiser_json['title']
        if fundraiser_json['fundraising_team'] is not None:
            fundraiser_label += " (" + fundraiser_json['fundraising_team']['name'] + ")"
        fundraisers[fundraiser_json['id']] = fundraiser_label

    return fundraisers.items()


def get_fundraiser(id, session):
    return get_json("fundraising-pages/" + str(id), session)


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

    # TODO: Not sure if the `member_*` means they have to match actual Classy accounts.
    email = donation_form.cleaned_data['email']
    phone = donation_form.cleaned_data['phone']

    address = donation_form.cleaned_data['address']
    city = donation_form.cleaned_data['city']
    state = donation_form.cleaned_data['state']
    zip = donation_form.cleaned_data['zip']

    anonymous = bool(donation_form.cleaned_data['anonymous'] == 'True')
    comment = donation_form.cleaned_data['comment']
    amount = float(donation_form.cleaned_data['amount'])  # float needed for JSON
    type = donation_form.cleaned_data['type']
    check_num = donation_form.cleaned_data['check_num']

    json_data = {
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
        "member_email_address": email,
        "member_phone": phone,
        "offline_payment_info": {
            "check_number": check_num,
            "payment_type": type,
            # TODO: Good enough for now.  However, working with Classy team on alternatives.
            "description": "unapproved"
        },
    }

    post_json("campaigns/" + str(campaign_id) + "/transactions", json_data, session)


def get_unapproved_donations(session):
    json_data = get_json(
        "organizations/" + os.environ['CLASSY_ORG_ID'] + "/transactions?"
        + "filter=status%3Dsuccess,offline_payment_info.description%3Dunapproved&with=offline_payment_info", session)

    return json_data['data']


def approve_donation(donation_id, session):
    # TODO: add additional metadata field to track the current admin user that accepted it
    json_data = {
        "offline_payment_info": {
            "description": "approved"
        }
    }

    put_json("transactions/" + str(donation_id), json_data, session)


def delete_donation(donation_id, session):
    json_data = {
        "status": "canceled"
    }

    put_json("transactions/" + str(donation_id), json_data, session)

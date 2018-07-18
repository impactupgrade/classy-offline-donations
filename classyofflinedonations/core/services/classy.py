import os
import requests
import time
from dateutil import parser, tz


def get_access_token(session):
    if 'CLASSY_TOKEN' not in session or 'CLASSY_TOKEN_EXP_TS' not in session\
            or time.time() >= session['CLASSY_TOKEN_EXP_TS']:
        set_access_token(session)

    # print("access token: " + session['CLASSY_TOKEN'])
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

    if response.status_code < 300:
        return True
    else:
        print("POST " + path + " failed: " + str(response.status_code) + " " + response.text)
        return False

    # print("https://api.classy.org/2.0/" + path)
    # print(json_data)
    # print(response.text)


def put_json(path, json_data, session):
    token = get_access_token(session)
    headers = {'Authorization': 'BEARER ' + token, 'Content-Type': 'application/json'}
    response = requests.put('https://api.classy.org/2.0/' + path, json=json_data, headers=headers)

    if response.status_code < 300:
        return True
    else:
        print("PUT " + path + " failed: " + str(response.status_code) + " " + response.text)
        return False

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

    fundraisers_json = get_json("organizations/" + os.environ['CLASSY_ORG_ID'] + "/fundraising-pages?filter=member_id="
                         + session['CLASSY_MEMBER_ID'] + "&with=fundraising_team", session)
    for fundraiser_json in fundraisers_json['data']:
        # TODO: organizations/*/fundraising-pages should support with=campaign, rather than this extra hit
        # TODO: cache?
        campaign_json = get_json("campaigns/" + str(fundraiser_json['campaign_id']), session)

        if campaign_json['status'] != 'active':
            continue

        fundraiser_label = fundraiser_json['title']

        if fundraiser_json['fundraising_team'] is not None:
            fundraiser_label += " (" + fundraiser_json['fundraising_team']['name'] + ")"

        fundraiser_label += " - " + campaign_json['name']

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


def create_donation(donation_form, session, current_username):
    page_id = int(donation_form.cleaned_data['fundraiser'])  # TODO: Can a ChoiceField be typed and return an int value?
    # TODO: May eventually support donations for whole teams, and would need 'fundraising_team_id' set
    campaign_id = int(get_fundraiser(page_id, session)['campaign_id'])

    first_name = donation_form.cleaned_data['first_name']
    last_name = donation_form.cleaned_data['last_name']

    company_name = donation_form.cleaned_data['company_name']

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
    donation_date = donation_form.cleaned_data['donation_date']

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
        "offline_payment_info": {
            "check_number": check_num,
            "payment_type": type,
            # TODO: Good enough for now.  However, working with Classy team on alternatives.
            "description": "under_review"
        },
        "metadata": {
            "offline_email_address": email,
            "offline_phone": phone,
            "offline_donation_date": donation_date,
            "created_by": current_username
        }
    }

    return post_json("campaigns/" + str(campaign_id) + "/transactions", json_data, session)


def get_under_review_donations(session):
    # TODO: organizations/*/transactions needs to support 'with' to get the fundraiser page + team + campaign,
    # instead of having to do it here...

    donations_json = get_json(
        "organizations/" + os.environ['CLASSY_ORG_ID'] + "/transactions?"
        + "filter=status%3Dsuccess,offline_payment_info.description%3Dunder_review&with=offline_payment_info", session)
    donations_data = donations_json['data']

    # TODO: cache
    for donation_data in donations_data:
        fundraising_page_id = donation_data['fundraising_page_id']
        page_json = get_json("fundraising-pages/" + str(fundraising_page_id) + "?with=fundraising_team,campaign", session)

        # format the date into the same format we're using in the form's datepicker
        created_at = parser.parse(donation_data['created_at'])
        created_at = created_at.replace(tzinfo=tz.tzutc())  # response is in UTC, but datetime is naive
        # TODO: make tz configurable
        donation_data['created_at'] = created_at.astimezone(tz.gettz('America/New_York')).strftime("%m/%d/%Y")

        # aggregate into the single payload
        donation_data['page'] = page_json

    return donations_data


def approve_donation(donation_id, session, current_username):
    json_data = {
        "offline_payment_info": {
            "description": "approved"
        },
        "metadata": {
            "approved_by": current_username
        }
    }

    return put_json("transactions/" + str(donation_id), json_data, session)


def unapprove_donation(donation_id, session, current_username):
    json_data = {
        "status": "canceled",
        "offline_payment_info": {
            "description": "unapproved"
        },
        "metadata": {
            "unapproved_by": current_username
        }
    }

    return put_json("transactions/" + str(donation_id), json_data, session)

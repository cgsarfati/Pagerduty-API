# Script to create a list of users given a CSV named "users.csv" in the format:
#
# name,email,role,address,type
# John Doe,john.doe@example.com,admin,5555555555,phone
# Jane Doe,jane.doe@example.com,user,5555555554,sms
#
# CLI Usage: ./create_users api_key email
#   api_key: Your PagerDuty API access Token
#   email: Your PagerDuty email address

import requests
import json
import csv
import sys

base_url = 'https://api.pagerduty.com/users'


def create_user(headers, email, payload):
    """Creates user. Returns user info."""

    # Add admin's email, NOT the user being added
    headers['From'] = email

    # Data is user info
    r = requests.post(base_url, headers=headers, data=json.dumps(payload))

    print 'User creation response code: ' + str(r.status_code)
    return r.json()['user']


def create_contact_method(headers, user_id, payload):
    """Creates contact method of user. Returns id."""

    # Alter base_url's endpoint
    url = base_url + '/' + user_id + '/contact_methods'

    r = requests.post(url, headers=headers, data=json.dumps(payload))

    print 'Contact method response code: ' + str(r.status_code)
    return r.json()['contact_method']['id']


def create_notification_rule(headers, user_id, payload):
    """Creates notification rule of user. Returns nothing."""

    # Alter base_url's endpoint
    url = base_url + '/' + user_id + '/notification_rules'

    r = requests.post(url, headers=headers, data=json.dumps(payload))

    print 'Notification rule response code: ' + str(r.status_code)
    return


def process_csv(headers, email):

    # Parse csv
    reader = csv.DictReader(open('users.csv'), fieldnames=('name', 'email', 'role', 'address', 'type'))
    reader.next()

    for row in reader:
        print 'Creating user: ' + row['name']

        # Add User
        user = {
            'name': row['name'],
            'email': row['email'],
            'role': row['role'],
            'type': 'user'  # optional
            }

        r = create_user(headers, email, user)
        user_id = r['id']

        # Add contact method
        if row['type'] == 'phone':
            contact_method = {
                'contact_method': {
                    'type': 'phone_contact_method',
                    'label': 'Mobile',
                    'address': row['address']
                    }
                }

        elif row['type'] == 'sms':
            contact_method = {
                'contact_method': {
                    'type': 'sms_contact_method',
                    'label': 'Mobile',
                    'address': row['address']
                    }
                }

        contact_method_id = create_contact_method(headers, user_id, contact_method)

        # Add notification rule
        notification_rule = {
            'notification_rule': {
                'type': 'assignment_notification_rule',
                'start_delay_in_minutes': 0,
                'contact_method': {
                    'id': contact_method_id,  # optional
                    'type': contact_method['contact_method']['type']
                    }
                }
            }

        create_notification_rule(headers, user_id, notification_rule)


if __name__ == '__main__':

    # HTTP Request Headers
    headers = {
        'Authorization': 'Token token=' + sys.argv[1],  # api key
        'Content-type': 'application/json',
        'Accept': 'application/vnd.pagerduty+json;version=2'
        }

    process_csv(headers, sys.argv[2])  # email

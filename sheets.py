from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '11mtdTRdD1wBvXwZ-jevjsHc_q1yccshunZ_k4bf4Kh0'
SAMPLE_RANGE_NAME = 'A3'

service = None
sheet = None


def init():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'other_cred.json', SCOPES)  # if this gives error, change line to credentials.json (user creds) then other_cred.json (service account credentials)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        global service
        global sheet
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
    except HttpError as err:
        print(err)


def get_users():
    # Column is A
    running = True
    getRange = "A5:A22"
    users = {}

    values = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=getRange).execute().get('values', [])
    for i in range(len(values)):
        if values[i]:
            current_quota = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                               range=f"I{5 + i}").execute().get('values', [])
            if current_quota:
                current_quota = current_quota[0][0]
            else:
                current_quota = "0"
            a = {values[i][0]: current_quota}
        else:
            a = {"": [""]}

        users = users | a
    return users


def add_user(name: str, rank: str):
    row = len(get_users()) + 3
    range_ = f"A{row}:B{row}"
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID, range=range_,
        valueInputOption="USER_ENTERED", body=
        {
            "range": range_,
            "values": [
                [name, rank]
            ]
        }
    ).execute()


# noinspection PyUnresolvedReferences
def add_quota(name: str, column):
    users = get_users()
    if name.lower() in [user.lower() for user in list(users.keys())]:

        i = list(users.keys()).index(name)

        _range = f"{column}{i + 5}"

        current = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range=_range).execute().get('values', [])
        if not current or current[0][0] == "EXCUSED" or current[0][0] == "/":
            current = 0
        else:
            current = int(current[0][0])
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, range=_range,
            valueInputOption="USER_ENTERED", body=
            {
                "range": _range,
                "values": [
                    [str(1 + current)]
                ]
            }
        ).execute()
    elif name.lower() in [user[0:len(name)].lower() for user in list(users.keys())]:
        check_set = [user[0:len(name)].lower() for user in list(users.keys())]
        if len(set(check_set)) != len(check_set):
            return "Too many users"
        i = check_set.index(name)
        _range = f"{column}{i + 5}"

        current = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                     range=_range).execute().get('values', [])
        if not current or current[0][0] == "EXCUSED" or current[0][0] == "/":
            current = 0
        else:
            current = int(current[0][0])
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID, range=_range,
            valueInputOption="USER_ENTERED", body=
            {
                "range": _range,
                "values": [
                    [str(1 + current)]
                ]
            }
        ).execute()
        return list(users.keys())[i]

    else:
        return "Not Found"

import datetime
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def create_service(creds):
    service = build('calendar', 'v3', credentials=creds)
    return service


def get_events(service):
    # now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary',
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def create_event(service, event):
    event = json.loads(event)
    event = service.events().insert(calendarId='primary', body=event,
                                    sendNotifications=True).execute()
    return event


def colored_events(service, colorId):
    events = get_events(service)
    colored_events = []
    for event in events:
        if "colorId" in event and event['colorId'] == colorId:
            colored_events.append(event)
    return colored_events


def conflict_events(service, cur_event):
    events = colored_events(service, "4")
    cur_event = json.loads(cur_event)

    for event in events:
        dc = date_conflict(event, cur_event)
        ac = attendees_conflict(event, cur_event)
        print(dc, ac)
        if dc:
            return True
    return False


def date_conflict(event, cur_event):
    event_start_time = datetime.datetime.strptime(
        event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    event_end_time = datetime.datetime.strptime(
        event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    cur_event_start_time = datetime.datetime.strptime(
        cur_event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    cur_event_end_time = datetime.datetime.strptime(
        cur_event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S%z')
    if cur_event_start_time >= event_start_time and cur_event_end_time <= event_end_time:
        return True
    return False


def attendees_conflict(event, cur_event):
    event_emails = set()
    cur_event_emails = set()
    if 'attendees' in event:
        for aten in event['attendees']:
            event_emails.add(aten['email'])
    if 'attendees' in cur_event:
        for aten in cur_event['attendees']:
            cur_event_emails.add(aten['email'])
    if len(event_emails) == 0 or len(cur_event_emails) == 0:
        return False
    if len(event_emails.intersection(cur_event_emails)) != 0:
        return True
    return False


def format_data(data):
    print(data.content_type)
    pass


creds = get_credentials()
service = create_service(creds)

if __name__ == '__main__':
    creds = get_credentials()
    service = create_service(creds)
    event = {
        'summary': 'with me the god',
        'location': 'heaven',
        'description': 'with me the god',
        'start': {
            'dateTime': '2020-06-01T01:30:00+05:30',
        },
        'end': {
            'dateTime': '2020-06-30T02:30:00+05:30',
        }
    }
    # create_event(service,event)
    get_events(service)

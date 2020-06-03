from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
import os
from credentials_service import service, conflict_events, create_event, colored_events, get_events, events_by_email
app = Flask(__name__)
CORS(app)

# colorId = 3 == student
# colorId = 4 == mentor

# def create_json(event):
#     json_object = {}
#     json_object['summary'] = event['summary']
#     json_object['description'] = event['description']
#     json_object['location'] = event['location']
#     dateTime = {}
#     dateTime['dateTime'] = event['start']+":00"+"+05:30"
#     json_object['start'] = dateTime
#     dateTime = {}
#     dateTime['dateTime'] = event['end']+":00"+"+05:30"
#     json_object['end'] = dateTime
#     data = []
#     for att in event['attendees']:
#         temp = {}
#         temp['displayName'] = att
#         temp['email'] = att+"@ento.com"
#         data.append(temp)
#     json_object['attendees'] = data
#     json_object['colorId'] = event['colorId']

#     return json_object


@app.route("/insert", methods=["POST"])
def insert_event():
    # parameter = dir(request)
    # print(parameter)
    # print(request.content_type)
    # format_data(request)
    event = request.data.decode()
    # event = json.loads(event)
    # event = create_json(event)

    try:
        is_conflict = conflict_events(service, event)
        if is_conflict:
            return {"status": 'unable to create event due to conflict'}
        else:
            status = create_event(service, event)
            return jsonify(status)
    except Exception:
        return {"status": 'unable to create event'}


@app.route("/event/<event_id>", methods=["GET"])
def get_event_by_id(event_id):
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        return jsonify(event)
    except Exception:
        return {"status": "unable to retrieve"}


@app.route("/delete/<event_id>", methods=["DELETE"])
def delete_event_by_id(event_id):
    try:
        event = service.events().delete(calendarId='primary',
                                        eventId=event_id, sendUpdates="all").execute()
        return {"status": "deleted"}
    except Exception:
        return {"status": "resource not found or unable to delete"}


@app.route("/allevents", methods=["GET"])
def get_all_events():
    try:
        events_result = service.events().list(calendarId='primary',
                                              ).execute()
        events = events_result.get('items', [])
        return jsonify(events)
    except Exception:
        return {"status": "unable to retrieve"}


@app.route("/update/<event_id>", methods=["PUT"])
def update_event(event_id):
    try:
        event = request.data.decode()
        event = json.loads(event)
        updated_event = service.events().update(
            calendarId='primary', eventId=event_id, body=event).execute()
        return jsonify(updated_event)
    except Exception:
        return {"status": "unable to update"}


@app.route("/myevents/<email_id>", methods=["GET"])
def get_events_by_email(email_id):
    try:
        my_events = events_by_email(service, email_id)
        return jsonify(my_events)
    except Exception:
        return {"status": "unable to retrieve"}


@app.route("/colors/<colorId>", methods=["GET"])
def get_event_by_color(colorId):
    try:
        events = colored_events(service, colorId)
        return jsonify(events)
    except Exception:
        return {"status": "unable to retrieve"}

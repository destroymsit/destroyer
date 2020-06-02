from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import json
import os
from flask_restful import Api
from credentials_service import *
app = Flask(__name__)
api = Api(app)
CORS(app)


@app.route("/insert", methods=["POST"])
def insert_event():
    # parameter = dir(request)
    # print(parameter)
    # print(request.content_type)
    # format_data(request)
    event = request.data.decode()
    try:
        is_conflict = conflict_events(service, event)
        if is_conflict:
            return jsonify({"status": 'unable to create event due to conflict'})
        else:
            status = create_event(service, event)
            return jsonify({"status": 'event created'})
    except Exception:
        return jsonify({"status": 'unable to create event'})


@app.route("/event/<event_id>", methods=["GET"])
def get_event_by_id(event_id):
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    return jsonify({"event": event})


@app.route("/event/<event_id>", methods=["DELETE"])
def delete_event_by_id(event_id):
    event = service.events().delete(calendarId='primary',
                                    eventId=event_id, sendUpdates="all").execute()
    return jsonify({"event": event})


@app.route("/allevents", methods=["GET"])
def get_all_events():
    events = get_events(service)
    return jsonify({"events": events})


@app.route("/update", methods=["PUT"])
def update_event():
    return {'colors': "true"}


@app.route("/colors/<colorId>", methods=["GET"])
def get_event_by_color(colorId):
    events = colored_events(service, colorId)
    return {colorId: events}

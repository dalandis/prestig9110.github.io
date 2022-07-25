from flask import Blueprint, render_template, g, jsonify, request
from flask_discord import requires_authorization
from hello import get_db, defaultParams, app, oauth, _sendRequest
from decorators import bearer_required
import json
import re
from utils import _getStatus

botApi = Blueprint('botApi', __name__, template_folder='templates')

@botApi.route("/bot_api/check_user/", methods=['POST'])
@bearer_required
def botApiCheckUser():
    try:
        reqJson = request.get_json()
    except:
        return jsonify( { "error": "json invalid " + reqJson, "status_code": 400, "success": "" } ), 400

    get_db()

    g.cursor.execute("SELECT username, status, tag, type, user_id FROM users WHERE username = %s or user_id = %s", ( reqJson["user"], reqJson["user"] ))
    user = g.cursor.fetchone()

    print(user)

    tag = json.loads(re.sub('[^A-Za-z0-9а-яА-Я{}\':,@._-]+', '', user["tag"]).replace("'",'"').replace("True", "true").replace("False", "false").replace("None", "null"))

    return jsonify({"success": "ok", "status_code": 200, "error": "", 
        "data": {
            "username": user["username"],
            "status": _getStatus(user["status"]),
            "tag": tag["username"] + "#" + tag["discriminator"],
            "type": "Лицензия" if user["type"] == 1 else "Пиратка",
            "discord_id": user["user_id"]
        } } ), 200

@botApi.route("/bot_api/accept_user/", methods=['POST'])
@bearer_required
def accept_user():
    try:
        reqJson = request.get_json()
    except:
        return jsonify( { "error": "json invalid " + reqJson, "status_code": 400, "success": "" } ), 400

    get_db()

    status = 2

    g.cursor.execute("SELECT password, type FROM users WHERE id = %s", ( reqJson["user"] ))
    password = g.cursor.fetchone()

    data = {
        "username" : username,
        "password" : password['password'],
        "type" : password['type']
    }

    response = _sendRequest('add_user', data)

    g.cursor.execute( "UPDATE users SET status = %s WHERE id = %s", (status, reqJson["user"]) )
    g.conn.commit()

    return jsonify({"success": "ok", "status_code": 200, "error": "", 
        "data": "" } ), 200
    
@botApi.route("/bot_api/deny_user/", methods=['POST'])
@bearer_required
def deny_user():
    try:
        reqJson = request.get_json()
    except:
        return jsonify( { "error": "json invalid " + reqJson, "status_code": 400, "success": "" } ), 400

    get_db()

    g.cursor.execute( "UPDATE users SET status = %s WHERE id = %s", (3, reqJson["user"]) )
    g.conn.commit()

    return jsonify({"success": "ok", "status_code": 200, "error": "", 
        "data": "" } ), 200
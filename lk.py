from flask import Blueprint, render_template, g, jsonify
from flask_discord import requires_authorization
from hello import get_db, defaultParams, app, oauth
from decorators import protect_route
# import json

lk = Blueprint('lk', __name__, template_folder='templates')

# @lk.route("/me/")
@lk.route("/api/me/")
@protect_route
def me():
    get_db()
    defaultParams()
    # перенести на клиент
    # пока такой костыль что бы как минимум не падало с 500
    try:
        guilds = oauth.request('/users/@me/guilds')
    except:
        guilds = {}

    gmg_ok = 0

    for guild in guilds:
        if guild['id'] == '723912565234728972':
            gmg_ok = 1

    g.cursor.execute("SELECT id, username, tag, status FROM users WHERE user_id = %s", ( str(g.user.id), ))
    user = g.cursor.fetchone()

    opUser = 0
    
    if str(g.user.id) in app.config["PERMISSIONS"]:
        opUser = 1

    g.cursor.execute("SELECT * FROM markers WHERE user = '" + str(g.user.id) + "'")
    markers = g.cursor.fetchall()

    # return render_template(
    #     'profile/me.html', 
    #     params  = g.params,
    #     gmg_ok  = gmg_ok,  
    #     user_id = user_id, 
    #     users   = users, 
    #     markers = markers, 
    #     opUser  = opUser,
    #     version = app.config["GAME_VERSION"]
    # )

    return jsonify( { 
        "params": g.params,
        "gmg_ok": gmg_ok,  
        "user": user, 
        "markers": markers, 
        "opUser": opUser,
        "version": app.config["GAME_VERSION"] 
    } )
    
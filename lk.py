from flask import Blueprint, render_template, g, jsonify, request
from flask_discord import requires_authorization
from hello import get_db, defaultParams, app, oauth
from decorators import protect_route
from utils import _getStatus, _is_numb
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

    g.cursor.execute("SELECT id, username, status FROM users WHERE user_id = %s", ( str(g.user.id), ))
    user = g.cursor.fetchone()

    opUser = 0
    
    if str(g.user.id) in app.config["PERMISSIONS"]:
        opUser = 1

    # g.cursor.execute("SELECT * FROM markers WHERE user = '" + str(g.user.id) + "'")
    # markers = g.cursor.fetchall()

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
        "discordUser": g.user.to_json(),
        # "markers": markers, 
        "opUser": opUser,
        "version": app.config["GAME_VERSION"] 
    } )

@lk.route("/api/get_markers/")
@protect_route
def get_markers():
    get_db()
    defaultParams()

    g.cursor.execute("SELECT * FROM markers WHERE user = '" + str(g.user.id) + "'")
    markers = g.cursor.fetchall()

    return jsonify( { 
        "markers": markers,
        "count": len(markers)
    } )

@lk.route("/api/get_marker/<marker_id>")
@protect_route
def get_marker(marker_id):
    if marker_id == 'new':
        return jsonify( { 
            "marker": {},
        } )
    
    get_db()
    defaultParams()

    g.cursor.execute("SELECT * FROM markers WHERE user = '" + str(g.user.id) + "' and id = " + marker_id)
    marker = g.cursor.fetchone()

    worldType = 'over'
    worldName = 'GMGameWorld - overworld'

    if marker['id_type']=='turquoise' or marker['id_type']=='orange' or marker['id_type']=='lime' or marker['id_type']=='pink' or marker['id_type']=='farm':
        worldType = 'nether'
        worldName = 'GMGameWorld-Nether - nether'
    if marker['id_type']=='end_portals' or marker['id_type']=='pixel_arts':
        worldType = 'the_end'
        worldName = 'GMGameWorld-TheEnd - end'
    
    marker['world_type'] = worldType
    marker['world_name'] = worldName

    return jsonify( { 
        "marker": marker,
    } )

@lk.route("/api/save_edit_markers", methods=['POST'])
@protect_route
def save_edit_markers():
    get_db()
    defaultParams()

    params = request.get_json()

    server      = params['server']
    id_type     = params['id_type']
    name        = params['name']
    x           = str(params['x'])
    y           = "64"
    z           = str(params['z'])
    description = params['description']
    markerID    = params['markerID']

    if not server or not id_type or not name or not x or not z or not description:
        return jsonify( { 'error': 'Не заполнены обязательные поля' } )

    if not _is_numb(x) or not _is_numb(y) or not _is_numb(z):
        return jsonify( { 'error': 'Координаты могут быть только число' } )

    if markerID == 'new':
        g.cursor.execute( 
            'INSERT INTO markers (id_type, x, y, z, name, description, user, server, flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                ( id_type, x, y, z, name, description, str(g.user.id), server, 1)
        )
    else:
        g.cursor.execute( 
            'UPDATE markers SET id_type = %s, x = %s, y = %s, z = %s, name = %s, description = %s, server = %s, flag = %s WHERE id = %s AND user = %s',
                ( id_type, x, y, z, name, description, server, 1, markerID, str(g.user.id) )
        ) 
    
    g.cursor.execute(
        'INSERT INTO queue (task, status, object) VALUES (%s, %s, %s)',
            ( 'update', 'new', id_type )
    )
    
    g.conn.commit()

    return jsonify({"data": "success"})

@lk.route("/api/delete_markers", methods=['POST'])
@protect_route
def delete_markers():
    get_db()
    defaultParams()

    params = request.get_json()

    if "markerID" not in params:
        return jsonify( { 'error': 'Нет ID' } )

    g.cursor.execute( 'DELETE FROM markers WHERE id = %s AND user = %s', (params["markerID"], str(g.user.id)) )  
    g.conn.commit()

    return jsonify({'data': 'Маркер удален'})

@lk.route("/api/get_territories")
@protect_route
def get_territories():
    get_db()
    defaultParams()

    g.cursor.execute("SELECT * FROM territories WHERE user = '" + str(g.user.id) + "'")
    territories = g.cursor.fetchall()

    return jsonify( { 
        "markers": territories,
        "count": len(territories)
    } )

@lk.route("/api/get_terr/<terr_id>")
@protect_route
def get_terr(terr_id):
    if terr_id == 'new':
        return jsonify( { 
            "territory": {},
        } )
    
    get_db()
    defaultParams()

    g.cursor.execute("SELECT * FROM territories WHERE id = %s", ( terr_id ) )
    terr = g.cursor.fetchone()

    worldName = 'GMGameWorld - overworld'

    if terr['world']=='farm':
        worldName = 'FarmWorld - overworld'
    
    terr['world_name'] = worldName

    return jsonify( { 
        "terr": terr
    } )
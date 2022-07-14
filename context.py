from hello import mysql, app, oauth, cache
from flask import g
from utils import _getTitle
import requests
import json

def get_token(refresh):
    if refresh:
        pprint(refresh)

        try:
            result = requests.post(
                app.config["JWT_URL"] + 'refresh', 
                data = {}, 
                headers = { 'Authorization' : 'Bearer ' + g.jwt_refresh_token }
            )
        except:
            return 'error_'

        if result.status_code == 401:
            get_token(refresh=0)
        
        tokens = result.json()

        pprint(tokens['access_token'])

        return tokens['access_token']
    else:
        data = {
            "username" : app.config["JWT_LOGIN"],
            "password" : app.config["JWT_PASS"]
        }

        try:
            result = requests.post(app.config["JWT_URL"] + 'login', json = data)
        except:
            return 'error_', 'error_'

        tokens = result.json()
        
        return tokens['access_token'], tokens['refresh_token']

def get_db():
    if 'conn' not in g:
        g.conn = mysql.connect()
    if 'cursor' not in g:
        g.cursor = g.conn.cursor()

def defaultParams():
    auth_ok = 0
    g.user = {}

    if oauth.authorized:
        auth_ok = 1
        g.user = oauth.fetch_user()

    resposeCache = cache.get('jhwvfkjwevhfhjwek' if app.config["DEV"] == "true" else 'responseCategory')

    if resposeCache is None:
        get_db()

        g.cursor.execute('SELECT * FROM category')
        resposeCache = g.cursor.fetchall()

        cache.set('jhwvfkjwevhfhjwek' if app.config["DEV"] == "true" else 'responseCategory', resposeCache, timeout=10800)

    g.jwt_token, g.jwt_refresh_token = get_token(refresh=0)

    g.params = {"user": g.user.to_json(), "auth_ok": auth_ok, "categories": resposeCache}

def getbreadcrumbs(page, **params):
    breadcrumbs = []

    if page == 'wiki':
        breadcrumbs.append({"name": page, "src": "#"})
        breadcrumbs.append({"name": _getTitle(params["category"]), "src": "/category/" + str(params["category"])})
        breadcrumbs.append({"name": params["title"], "src": "/article/" + str(params["id"])})
    
    # if page == "category":
    #     breadcrumbs.append({"name": "wiki", "src": "#"})

    #     resposeCache = cache.get('jhwvfkjwevhfhjwek' if app.config["DEV"] == "true" else 'responseCategory')
    
    #     for category in resposeCache:
    #         if int(category["id"]) == int(params["category"]):
    #             breadcrumbs.append({"name": category["name_category"], "src": "/category/" + str(params["category"])})

    return breadcrumbs
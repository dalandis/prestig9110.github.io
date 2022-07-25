from hello import app, cache

def _is_numb ( digit ):
    return digit.isdigit() if digit[:1] != '-' else digit[1:].isdigit()

def _allowed_file(filename):
    allowed_types = set(["png", "jpg", "jpeg", "gif"])
    print("Check if image types is allowed")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_types

def _getTitle(ids):
    resposeCache = cache.get('jhwvfkjwevhfhjwek' if app.config["DEV"] == "true" else 'responseCategory')
    
    for category in resposeCache:
        if int(category["id"]) == int(ids):
            return category["name_category"]

def _getStatus(id):
    status = "Новый игрок"

    if id == 2:
        status = "Игрок сервера"
    if id == 3:
        status = "Отказано"
    if id == 4:
        status = "Забанен"
    if id == 5:
        status = "Не в вайтлисте"

    return status
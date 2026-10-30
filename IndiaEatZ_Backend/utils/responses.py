from flask import jsonify

def error(message, status=400, **extra):
    return jsonify({"success": False, "message": message, **extra}), status

def success(message, data=None, status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status

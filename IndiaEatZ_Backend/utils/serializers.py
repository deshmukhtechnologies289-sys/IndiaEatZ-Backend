from bson import ObjectId

def serialize_doc(doc):
    if not doc:
        return None
    result = dict(doc)
    result["id"] = str(result.pop("_id"))
    for key, value in list(result.items()):
        if isinstance(value, ObjectId):
            result[key] = str(value)
    return result

def public_user(user):
    if not user:
        return None
    return {"id": str(user["_id"]), "name": user.get("name"),
            "email": user.get("email"), "role": user.get("role", "customer")}

import pymongo
from datetime import datetime, timedelta, timezone
from shared.config import TRAINING_QUEUE_LIMIT_DURATION, MONGO_USER, MONGO_PWD, MONGO_HOST


client = pymongo.MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PWD}@{MONGO_HOST}:27017")
db = client["hil_prototype"]


def clear_database():
    """
    Clears the MongoDB database by deleting the training queue, all data and list collections,
    and all users except the admin.
    Returns:
        bool: True if the database is successfully cleared, False otherwise.
    """
    try:
        # delete training queue
        db["training_queue"].drop()

        # delete all data and list collections
        for collection in db.list_collection_names():
            if collection.startswith("data_") or collection.startswith("list_"):
                db[collection].drop()

        # delete all users except admin
        db["users"].delete_many({"role": {"$ne": "admin"}})

        return True
    

    except Exception as e:
        print("Error in reset_mongodb")
        print(e)
        return False


def insertOne(collection, document):
    """
    Insert a single document into the specified collection.
    Parameters:
    - collection (str): The name of the collection to insert the document into.
    - document (dict): The document to be inserted.
    Returns:
    - None
    """

    db[collection].insert_one(document)


def db_check_if_token_blacklisted(jiti: str) -> bool:
    """
    Check if a token is blacklisted in the database.
    Parameters:
    - jiti (str): The token to check.
    Returns:
    - bool: True if the token is blacklisted, False otherwise.
    """

    document = db["blacklisted_tokens"].find_one({"jiti": jiti})
    return document is not None


def delete_user_from_db(username: str) -> bool:
    """
    Deletes a user from the database.
    Args:
        username (str): The username of the user to be deleted.
    Returns:
        bool: True if the user was successfully deleted, False otherwise.
    """

    result = db["users"].delete_one({"username": username})
    return result.deleted_count > 0


def db_change_password(username: str, hashed_new_password: str) -> bool:
    """
    Change the password of a user in the database.
    Args:
        username (str): The username of the user.
        hashed_new_password (str): The hashed new password.
    Returns:
        bool: True if the password was successfully changed, False otherwise.
    """
    
    result = db["users"].update_one(
        {"username": username}, {"$set": {"password_hash": hashed_new_password}}
    )
    return result.modified_count > 0



def get_user_passwordhash(username: str) -> str:
    """
    Retrieves the password hash for a given username.
    Args:
        username (str): The username to retrieve the password hash for.
    Returns:
        str: The password hash for the given username, or None if the username does not exist.
    """

    document = db["users"].find_one({"username": username})

    if document is None:
        return None

    return document["password_hash"]


def get_all_users() -> list:
    """
    Retrieves all users from the database.
    Returns:
        list: A list of dictionaries representing the users.
    """

    return list(db["users"].find({}, {"_id": 0, "password_hash": 0}))

def get_user_role(username: str) -> str:
    """
    Retrieves the role of a user based on their username.
    Parameters:
    - username (str): The username of the user.
    Returns:
    - str: The role of the user. If the user does not exist or the role is not found, "user" is returned.
    """

    document = db["users"].find_one({"username": username})

    if document is None:
        return None
    try:
        return document["role"]
    except KeyError:
        return "user"

def get_train_queue_count(userid: str):
    """
    Get the count of training queue entries for a specific user within a specified time range.
    Useful to check if the user has too many training tasks in the queue.
    Args:
        userid (str): The ID of the user.
    Returns:
        int: The count of training queue entries.
    """

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=TRAINING_QUEUE_LIMIT_DURATION)

    query = {"user": userid, "date": {"$gte": cutoff, "$lte": now}}
    return db["training_queue"].count_documents(query)


def get_date_end_for_model(userid: str, modeltype: str) -> datetime:
    """
    Retrieves the end date for a specific model type belonging to a user.
    Used to determine the date range for training data (find out which data was already used for training).
    Args:
        userid (str): The ID of the user.
        modeltype (str): The type of the model.
    Returns:
        datetime: The end date of the model.
    """

    collection = db[f"list_{userid}"]
    document = collection.find_one(
        {"modeltype": modeltype}, sort=[("date", pymongo.DESCENDING)]
    )

    if document is None:
        return None

    return datetime.fromisoformat(document["date"])


def get_data_for_interval(userid: str, dateStart: datetime, dateEnd: datetime) -> list:
    """
    Retrieves data that a given user contributed within within a specified date interval.
    Args:
        userid (str): The ID of the user.
        dateStart (datetime): The start date of the interval.
        dateEnd (datetime): The end date of the interval.
    Returns:
        list: A list of data within the specified date interval.
    """

    print("get_data_for_interval")
    collection = db[f"data_{userid}"]

    print("range:", dateStart, dateEnd)

    criteria = {
        "postedOn": {"$gte": dateStart, "$lte": dateEnd}
    }

    criteria = {}

    returnlist = []
    documents = collection.find(criteria)

    for el in documents:
        returnlist.append(el["data"])

    return returnlist

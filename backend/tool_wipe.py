import pika
import pymongo
import os
import shutil
from shared.config import MONGO_USER, MONGO_PWD

connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()

channel.queue_delete(queue='prediction')
channel.queue_delete(queue='annotated_data')
channel.queue_delete(queue="new_training")

connection.close()

# https://kb.objectrocket.com/mongo-db/how-to-delete-mongodb-collections-using-python-354
client = pymongo.MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PWD}@localhost:27017")
db = client["hil_prototype"]


# delete all data and list collections
for collection in db.list_collection_names():
    if collection.startswith("data_") or collection.startswith("list_"):
        db[collection].drop()

# delete all users except admin
db["users"].delete_many({"role": {"$ne": "admin"}})


#db["data_TESTUSER"].drop()
#db["list_TESTUSER"].drop()

if os.path.exists("data_TESTUSER"):
    shutil.rmtree("data_TESTUSER")
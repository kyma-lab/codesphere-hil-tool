import pymongo
from datetime import datetime, timedelta, timezone
from config import TRAINING_QUEUE_LIMIT_DURATION, MONGO_USER, MONGO_PWD


def insertOne(collection, document):
    db[collection].insert_one(document)


client = pymongo.MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PWD}@localhost:27017")
db = client["hil_prototype"]

create = False

if create:
    for i in range(0, 23):
        document = {
            "userid": "test",
            "data": i,
            "postedOn": datetime.now() + timedelta(hours=i),
        }

        insertOne("testcollection", document)


startTime = datetime.now() + timedelta(hours=0)
endTime = datetime.now() + timedelta(hours=2)

criteria = {
    "$and": [{"postedOn": {"$gte": startTime, "$lte": endTime}}, {"userid": "test"}]
}

criteria = {
    "postedOn": {"$gte": startTime, "$lte": endTime}
}

result = db["testcollection"].find(criteria)

for el in result:
    print(el["data"])

quit()

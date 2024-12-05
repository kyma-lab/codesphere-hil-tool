import pymongo
import os
import json
from shared.config import MONGO_USER, MONGO_PWD

# https://kb.objectrocket.com/mongo-db/how-to-delete-mongodb-collections-using-python-354
client = pymongo.MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PWD}@localhost:27017")
db = client["hil_prototype"]


# Function to download (export) a MongoDB collection
def export_collection(collection_name, output_file):
    collection = db[collection_name]
    data = list(collection.find())
    
    # Write data to JSON file
    with open(output_file, 'w') as file:
        json.dump(data, file, default=str)  # default=str to handle ObjectId and datetime serialization

# Download the bpmn collection
export_collection("bpmn", "bpmn_collection.json")

# Download the data_Studie2024 collection
export_collection("data_Studie2024", "data_Studie2024_collection.json")

print("Collections have been exported successfully.")
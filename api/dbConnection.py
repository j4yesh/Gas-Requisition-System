import pymongo
from dotenv import load_dotenv
import os
load_dotenv()


client=pymongo.MongoClient(os.getenv('DB_URL'))

db=client['gasutility']
if(client):
    print("dbConnected")

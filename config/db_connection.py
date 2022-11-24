import pymongo as pymongo
from pymongo.server_api import ServerApi

# Mongo Db Atlas connection
# pymongo
from Clabs.settings import connection_string

client = pymongo.MongoClient(connection_string, server_api=ServerApi('1'))
db = client["Clabs"]

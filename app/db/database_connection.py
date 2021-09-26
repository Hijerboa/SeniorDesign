from pymongo import MongoClient
from util.cred_handler import get_secret


def get_connection():
    """
    Creates a database connection
    :return: a db connection object
    """

    connection_string = 'mongodb://mongo:27017'
    client = MongoClient(connection_string)
    db = client[get_secret('mongo_database')]
    return db
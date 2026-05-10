from config.settings.base import MONGODB_NAME, MONGODB_URI
from mongoengine import connect

def init_mongo():
    return connect(db=MONGODB_NAME, host=MONGODB_URI)

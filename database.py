import config
import jsonpickle
import os

class Database:
    def __init__(self, raw_db):
        self.__raw_db = raw_db


    def get_server_messages(self):
        return self.__raw_db["server_messages"]


    __DEFAULT_RAW_DB = {
        "server_messages": set(),
    }


    def load():
        '''Returns the database.'''
        if not os.path.exists(config.DATABASE_FILENAME):
            Database(Database.__DEFAULT_RAW_DB).save() # empty DB
        with open(config.DATABASE_FILENAME, "r") as f:
            db = jsonpickle.loads(f.read())

        return Database(db)


    def save(self):
        '''Saves the specified database.'''
        jsonpickle.set_encoder_options("simplejson", indent=4, sort_keys=True)
        with open(config.DATABASE_FILENAME, "w") as f:
            f.write(jsonpickle.dumps(self.__raw_db))

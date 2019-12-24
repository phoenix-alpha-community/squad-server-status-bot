import config
import jsonpickle
import os

class Database:
    def __init__(self):
        self.server_messages = set()


    def load():
        '''Returns the database.'''
        if not os.path.exists(config.DATABASE_FILENAME):
            Database().save() # empty DB
        with open(config.DATABASE_FILENAME, "r") as f:
            db = jsonpickle.loads(f.read())

        return db


    def save(self):
        '''Saves the specified database.'''
        jsonpickle.set_encoder_options("json", indent=4, sort_keys=True)
        jsonpickle.set_preferred_backend("json")
        with open(config.DATABASE_FILENAME, "w") as f:
            f.write(jsonpickle.dumps(self))

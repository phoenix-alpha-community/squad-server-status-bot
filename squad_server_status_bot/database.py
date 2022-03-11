import sys

import ZODB
import persistent
import transaction

import config


class _Database(persistent.Persistent):
    def __init__(self):
        self.squad_server_message_ids = persistent.list.PersistentList()
        self.post_server_message_ids = persistent.list.PersistentList()


sys.stdout.write("Starting database...")
connection = ZODB.connection(config.DATABASE_FILENAME)
root = connection.root
if not hasattr(root, "db"):
    database = _Database()
    root.db = database
    transaction.commit()

sys.stdout.write("done\n")
db = root.db

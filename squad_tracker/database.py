import BTrees
import config
import persistent
import sys
import transaction
import ZODB
from BTrees.OOBTree import TreeSet
from dataclasses import dataclass

class _Database(persistent.Persistent):

    def __init__(self):
        self.server_messages = persistent.list.PersistentList()


sys.stdout.write("Starting database...")
connection = ZODB.connection(config.DATABASE_FILENAME)
root = connection.root
if not hasattr(root, "db"):
    database = _Database()
    root.db = database
    transaction.commit()

sys.stdout.write("done\n")
db = root.db

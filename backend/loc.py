import sys
import os

sys.path.append(os.path.dirname(__file__))

from database.db_connection import db
import inspect

print(f"DATABASE MODULE LOCATION:")
print(inspect.getfile(db.__class__))

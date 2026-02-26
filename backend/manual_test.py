import sys
import os

sys.path.append(os.path.dirname(__file__))

from database.db_connection import db

# Simulate what `login` route does
email = "test@test.com"
print("Executing search query...")
user = db.execute_query(
    collection='users',
    mongo_query={'email': email}
)

print(f"Result type: {type(user)}")
print(f"Result: {user}")

if not user or len(user) == 0:
    print("User not found.")
else:
    u = user[0]
    print(f"First user type: {type(u)}")
    print(f"Trying to access user.get('_id'): {u.get('_id')}")

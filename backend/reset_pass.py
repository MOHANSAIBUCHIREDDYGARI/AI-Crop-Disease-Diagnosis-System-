import sys, os, bcrypt
sys.path.append(os.getcwd())
try:
    from database.db_connection import db

    password = 'password123'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users = db.execute_query(collection='users', mongo_query={})
    for u in users:
        email = u.get('email')
        db.execute_update(collection='users', mongo_query={'email': email}, update={'password_hash': hashed})
        print(f'Updated password for {email}')
except Exception as e:
    print(e)

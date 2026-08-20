import sqlite3, os

db = r"C:\Users\vinay\Desktop\BlogCreation\db.sqlite3"
media_dir = r"C:\Users\vinay\Desktop\BlogCreation\media\profile_pics"

if not os.path.exists(db):
    print('DB not found:', db)
    raise SystemExit(1)

con = sqlite3.connect(db)
cur = con.cursor()

print('Files in', media_dir)
if os.path.exists(media_dir):
    for f in sorted(os.listdir(media_dir)):
        print('-', f)
else:
    print('media/profile_pics does not exist')

try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users_profile'")
    if not cur.fetchone():
        print('users_profile table not found')
    else:
        cur.execute("SELECT id, image FROM users_profile")
        rows = cur.fetchall()
        print('\nProfile image entries:')
        for r in rows:
            print(f'id={r[0]} image={r[1]}')
finally:
    con.close()

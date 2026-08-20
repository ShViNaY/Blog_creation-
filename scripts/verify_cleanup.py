import sqlite3, os
DB = r"C:\Users\vinay\Desktop\BlogCreation\db.sqlite3"
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("SELECT id, image FROM users_profile ORDER BY id")
rows = cur.fetchall()
print('Current profile rows:')
for r in rows:
    print(r)
con.close()
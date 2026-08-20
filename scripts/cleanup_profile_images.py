import sqlite3, os, zipfile, datetime

BASE = r"C:\Users\vinay\Desktop\BlogCreation"
DB = os.path.join(BASE, 'db.sqlite3')
MEDIA_DIR = os.path.join(BASE, 'media', 'profile_pics')
BACKUP = os.path.join(BASE, 'media', f'profile_pics_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')

PROTECTED_FILENAMES = {'ADMIN.jpg'}
PROTECTED_DB_VALUES = {'profile_pics/ADMIN.jpg', 'default.jpg', 'profile_pics/default.jpg'}

if not os.path.exists(DB):
    print('DB not found:', DB)
    raise SystemExit(1)

if not os.path.exists(MEDIA_DIR):
    print('media/profile_pics directory not found:', MEDIA_DIR)
    raise SystemExit(1)

# Backup files before removing
with zipfile.ZipFile(BACKUP, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for fname in os.listdir(MEDIA_DIR):
        path = os.path.join(MEDIA_DIR, fname)
        if os.path.isfile(path):
            zf.write(path, arcname=fname)
print('Backup created at', BACKUP)

# Connect to DB
con = sqlite3.connect(DB)
cur = con.cursor()

# Find profile entries and update those that reference non-protected images
cur.execute("SELECT id, image FROM users_profile")
rows = cur.fetchall()
updated = []
for rid, img in rows:
    if not img:
        continue
    if img in PROTECTED_DB_VALUES:
        continue
    # Update to default.jpg
    cur.execute("UPDATE users_profile SET image = ? WHERE id = ?", ('default.jpg', rid))
    updated.append((rid, img))
con.commit()

# Delete files in media/profile_pics except protected
deleted_files = []
for fname in os.listdir(MEDIA_DIR):
    if fname in PROTECTED_FILENAMES:
        continue
    path = os.path.join(MEDIA_DIR, fname)
    if os.path.isfile(path):
        try:
            os.remove(path)
            deleted_files.append(fname)
        except Exception as e:
            print('Failed to remove', path, e)

print('\nDB rows updated (set to default.jpg):')
for u in updated:
    print('-', u)

print('\nFiles deleted:')
for f in deleted_files:
    print('-', f)

print('\nDone.')
con.close()

import os, sys
sys.path.insert(0, r'D:\BlogCreation')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()
username = 'Admin'
try:
    u = User.objects.get(username=username)
except User.DoesNotExist:
    print('ERROR: user not found')
    raise SystemExit(1)

perms_added = []
# delete_user permission (auth.User)
pu = Permission.objects.filter(codename='delete_user').first()
if pu:
    if not u.has_perm('auth.delete_user'):
        u.user_permissions.add(pu)
        perms_added.append('auth.delete_user')
else:
    print('WARN: delete_user permission not found')

# delete_post permission (blog.Post)
pp = Permission.objects.filter(codename='delete_post').first()
if pp:
    # determine app_label and codename to check
    key = f"{pp.content_type.app_label}.delete_{pp.content_type.model}"
    if not u.has_perm(key):
        u.user_permissions.add(pp)
        perms_added.append(key)
else:
    print('WARN: delete_post permission not found; available delete perms:')
    for p in Permission.objects.filter(codename__startswith='delete_')[:50]:
        print('-', p.content_type.app_label, p.codename)

u.save()
print('USER:', u.username, 'is_superuser=', u.is_superuser, 'is_staff=', u.is_staff)
if perms_added:
    print('ADDED_PERMISSIONS:', perms_added)
else:
    print('NO_NEW_PERMISSIONS_ADDED')

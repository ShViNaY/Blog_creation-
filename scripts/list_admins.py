import os
import sys
# ensure project root is on sys.path so Django settings module can be imported
sys.path.insert(0, r'D:\BlogCreation')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()
from django.contrib.auth.models import User
import json
admins = User.objects.filter(is_superuser=True)
if admins.exists():
    out = [{'username':u.username, 'email':u.email, 'is_active':u.is_active} for u in admins]
    print(json.dumps(out))
else:
    print('NO_SUPERUSERS')

#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-create a superuser on free tier since render shell is disabled
if [[ $CREATE_SUPERUSER == "true" ]]; then
  python manage.py shell -c "
import os
import django

from accounts.models import CustomUser

username = os.environ.get('RENDER_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('RENDER_SUPERUSER_PASSWORD', 'admin123')

if not CustomUser.objects.filter(username=username).exists():
    CustomUser.objects.create_superuser(username=username, email='admin@example.com', password=password)
else:
    u = CustomUser.objects.get(username=username)
    u.set_password(password)
    u.save()
"
fi

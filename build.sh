#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirement.txt

python manage.py collectstatic --no-input
python manage.py migrate

gunicorn GasUtility.wsgi:application --bind 0.0.0.0:8000



# #!/usr/bin/env bash
# # exit on error
# set -o errexit

# pip install -r requirement.txt

# python manage.py collectstatic --no-input
# python manage.py migrate
# if [[ $CREATE_SUPERUSER ]]; then
#   python manage.py createsuperuser --no-input --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
# fi

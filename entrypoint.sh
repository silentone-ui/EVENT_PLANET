#!/bin/sh
set -e

echo "Waiting for DB $DB_HOST:$DB_PORT..."
python -c "import socket,time,os; h=os.getenv('DB_HOST','db'); p=int(os.getenv('DB_PORT','5432')); [__import__('time').sleep(2) for _ in range(30) if __import__('socket').socket().connect_ex((h,p))!=0]"

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
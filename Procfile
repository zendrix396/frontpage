web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && uvicorn frontpage.asgi:application --host=0.0.0.0 --port=${PORT:-8000}

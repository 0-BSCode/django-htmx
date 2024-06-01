# !usr/bin/env bash

echo "Installing python dependencies..."
pip3 install -r requirements.txt

echo "Collecting static files..."
python3 manage.py collectstatic --no-input

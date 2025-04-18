#!/bin/bash

# Check Python version
if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "Python is not installed. Please install Python 3 and try again."
  exit 1
fi

echo "Creating virtual environment"
$PYTHON -m venv env

echo "Activating virtual environment"
source env/bin/activate

echo "Installing Python packages"
pip install --upgrade pip
pip install -r requirements.txt

ENV_PATH="./backend/.env"

if [ ! -f "$ENV_PATH" ]; then
  echo "Creating .env file in backend/"
  cat <<EOT >> "$ENV_PATH"
# ALLOWED_HOSTS=127.0.0.1,localhost
# DATABASE_URL=postgres://user:password@localhost:5432/dbname
USER_REGISTRATION_ENABLED=True
EOT
else
  echo ".env file already exists in backend/. Skipping"
fi

echo "Running migrations"
cd backend
$PYTHON manage.py migrate

echo ""
echo "Project setup complete"
echo ""
echo "To activate the virtual environment, run:"
echo "source env/bin/activate"
echo ""
echo "To deactivate the virtual environment, run:"
echo "deactivate"
echo ""
echo "To run the server, use:"
echo "cd backend"
echo "uvicorn backend.asgi:application --host 0.0.0.0 --port 8000"

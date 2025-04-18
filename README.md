# Django Game Server Manager

A Django-based backend application for managing and monitoring game server processes in real time.

## Requirements

- Python 3
- Git

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/deljanin/game-server-manager-backend.git
cd game-server-manager-backend
```

2. Run the setup script

   This will:

   - Create a virtual environment
   - Install required packages
   - Run migrations to setup the database
   - Create a .env file in backend/ with `USER_REGISTRATION_ENABLED=True`

   #### ⚠️ Important: Set this USER_REGISTRATION_ENABLED to false after creating your user and restart your server

```bash
chmod +x setup.sh
./setup.sh
```

3. Run the server
   - To activate the virtual environment, run:<br>
   ```bash
   source env/bin/activate
   ```
   - To deactivate the virtual environment, run:<br>
   ```bash
   deactivate
   ```
   - To run the server, use:<br>
   ```bash
   cd backend
   uvicorn backend.asgi:application --host 0.0.0.0 --port 8000
   ```

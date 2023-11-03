# Airport API 

API service system for tracking flights from airports across the whole globe written on DRF


## Installing using GitHub
Install PostgresSQL and create db

Python3 must be already installed

```shell
git clone https://github.com/IProskurnytskyi/airport-api-servicer
cd airport_api_service
git checkout develop
python -m venv venv
if macOS: source venv/bin/activate
if Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
Copy .env.sample > .env and populate with all required data
python manage.py migrate
python manage.py runserver
```
You have to create .env file and set all required environment variables!

## Run with Docker
Docker must be installed

```shell
Copy .env.sample > .env and populate with all required data
docker-compose up --build
```

## Getting access
* create user via /api/user/register
* get access token via /api/user/token
* look for documentation via /api/doc/swagger
* admin panel via /admin

## Features
* Creating airports with image
* Filtering flights and routs
* Managing orders and tickets
* JWT Authentication
* New permission classes
* Using email instead of username
* Throttling
* API documentation
* Tests
* Docker

# Contributing

If you'd like to contribute, please fork the repository and use a develop branch. 
Pull requests are warmly welcome.

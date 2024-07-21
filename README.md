# Taxi Backend

Backend for Taxi


## Development Environment Setup

Create local virtual environment and database

    python3 -m venv .venv
    pip install -r requirements.txt
    createuser -P --interactive taxi
    createdb -O taxi db_taxi
    CREATE EXTENSION postgis;

To run app

    python3 run.py
    http://127.0.0.1:5055/docs

_Note_: use `ExpressTaxi.` as password while creating local user.

# Taxi Backend

Backend for Taxi


## Development Environment Setup

Create local virtual environment and database

    python3 -m venv .venv
    pip install -r requirements.txt
    createuser -P --interactive taxi
    createdb -O taxi db_taxi

To run app

    python3 run.py

_Note_: use `ExpressTaxi.` as password while creating local user.

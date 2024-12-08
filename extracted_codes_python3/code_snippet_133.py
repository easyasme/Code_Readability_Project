#!/usr/bin/env python

import sys
import os
import click

SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
sys.path.append(SRC_DIR)

from core.users import user_entities
from core.users import user_validators
from core.users import user_actions
from core.ideas import idea_entities
from core.ideas import idea_actions
from core.projects import project_entities
from core.projects import project_actions


@click.group()
def cli():
    pass


@cli.command()
def runserver():
    """
    Runs the local testing webserver.
    """
    from web.server import runserver
    runserver()


@cli.command()
def db_init():
    """
    Creates all tables if needed, and empty the database.
    """
    from services.repository.sql import repo
    repo.create_all_tables()
    repo.truncate_all_tables()
    print("Database initialized and cleared.")


@cli.command()
def sample_data():
    """
    Generate some random data for testing.
    """
    from core.sample_data import SampleData
    sample_data = SampleData()
    sample_data.run()


@cli.command()
@click.argument("username", nargs=1, type=click.STRING)
@click.argument("password", nargs=1, type=click.STRING)
@click.argument("full_name", nargs=1, type=click.STRING)
@click.argument("email", nargs=1, type=click.STRING)
def create_user(username, password, full_name, email):
    """
    Register a new user in the system.
    """
    validator = user_validators.UserForRegisterValidator({
        "username": username,
        "clear_password": password,
        "full_name": full_name,
        "email": email,
    })
    if validator.is_valid():
        user = user_actions.register_new_user(
            user_entities.UserForRegister(**validator.cleaned_data)
        )
        print("Created user {}".format(user.username))
    else:
        for key, error in validator.errors.items():
            print("Error in {}: {}".format(key, error))


if __name__ == "__main__":
    cli()

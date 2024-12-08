#!/usr/bin/env python3

import argparse
import subprocess, os

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser.add_argument("--test", required=False, action='store_true')
parser.add_argument("--run", required=False, action='store_true')

parser.add_argument("--local", required=False, action='store_true')
parser.add_argument("--docker", required=False, action='store_true')

args, leftovers = parser.parse_known_args()

is_docker = args.docker
is_local = args.local

is_run = args.run
is_test = args.test

is_prod = not(is_docker or is_local)

if (is_docker and is_local):
    print("Must select ONE of local or docker, but not both")
    exit(1)

if (is_run and is_test):
    print("Must select ONE of run or test, but not both")
    exit(1)
    
env = os.environ.copy()

env["DATASTORE_DATASET"] = "malleus-local"
env["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
env["DATASTORE_EMULATOR_HOST_PATH"] = "localhost:8081/datastore"
env["DATASTORE_HOST"] = "http://localhost:8081"
env["DATASTORE_PROJECT_ID"] = "malleus-local"
env["MONGODB_HOST"] = "localhost:27017"
env["PYTHONPATH"] = "./"

if is_test:
    if is_local:
        subprocess.Popen(["pytest", "malleus/tests"],env=env).wait()
    if is_docker:
        # TODO: What if docker image is not built?
        cmd = "docker-compose up --abort-on-container-exit "
        subprocess.Popen(cmd.split()).wait() #TODO: Does ctrl-c kill this process?
if is_run:
    if is_local:
        subprocess.Popen(["python","malleus/api/server.py"],env=env).wait()

# if is_clean:
#    find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
#!/usr/bin/env python3
import sys
import importlib.util
import os

def fetch_script_name():
    if len(sys.argv) > 0:
        # The first argument (index 0) is the script name
        script_name = sys.argv[0]

        return script_name
    else:
        print("No script name provided which should never happen but fuck it.")

def     fetch_module_name():
    if len(sys.argv) > 1:
        command_name = sys.argv[1]
        return command_name
    else:
        print("No command line arguments provided.")

def fetch_command_name():
    if len(sys.argv) > 2:
        command_name = sys.argv[2]
        return command_name
    else:
        print("No command argument provided.")

def fetch_command_arguments():
    arguments = sys.argv[3:]
    return arguments


def import_command_class(module, command_name):
    try:
        command_class = getattr(module, command_name)
        return command_class
    except AttributeError:
        print("Comannd '{}' not found on module.".format(command_name))
        sys.exit()

def import_module(module_name):
    try:
        # Get the absolute path to the module
        module_path = os.path.join("commands", module_name + ".py")
        # Generate the module spec
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        # Create the module from the spec
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        print("Module '{}' not found.".format(module_name))
        return None


script_name = fetch_script_name()
module_name = fetch_module_name()
command_name = fetch_command_name()
command_arguments = fetch_command_arguments()

module = import_module(module_name)

command_class = import_command_class(module, command_name)



command_class(command_arguments)
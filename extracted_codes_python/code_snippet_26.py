#!/usr/bin/python3
import cmd
from models.base_model import BaseModel
from models import storage
import uuid

class HBNBCommand(cmd.Cmd):
    """Command interpreter for the AirBnB project.
    This class handles the command line interface for managing
    AirBnB objects. It supports commands like quit, EOF, help, create, show, destroy, all, and update.
    """

    prompt = '(hbnb) '

    def do_quit(self, line):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, line):
        """Exit the program when EOF (Ctrl+D) is encountered."""
        return True

    def do_help(self, line):
        """Display help information about commands."""
        if line:
            if hasattr(self, 'do_' + line):
                func = getattr(self, 'do_' + line)
                print(self._get_help(func))
            else:
                print("*** No help on {}".format(line))
        else:
            super().do_help(line)

    def emptyline(self):
        """Override the emptyline method to do nothing on an empty input line."""
        pass

    def _get_help(self, func):
        """Helper method to get the help string for a command function."""
        doc = func.__doc__
        return doc if doc else "No help available."

    def do_create(self, line):
        """Create a new instance of BaseModel, save it (to the JSON file) and print the id.
        Usage: create <class name>
        """
        if not line:
            print("** class name missing **")
            return
        try:
            cls = eval(line)
            if not issubclass(cls, BaseModel):
                print("** class doesn't exist **")
                return
            instance = cls()
            instance.save()
            print(instance.id)
        except Exception as e:
            print("** class doesn't exist **")

    def do_show(self, line):
        """Print the string representation of an instance based on the class name and id.
        Usage: show <class name> <id>
        """
        args = line.split()
        if len(args) == 0:
            print("** class name missing **")
            return
        try:
            cls = eval(args[0])
            if not issubclass(cls, BaseModel):
                print("** class doesn't exist **")
                return
            if len(args) == 1:
                print("** instance id missing **")
                return
            instance_id = args[1]
            key = "{}.{}".format(class_name, instance_id)
            instance = storage.all().get(key)
            if instance is None:
                print("** no instance found **")
            else:
                print(instance)
        except Exception as e:
            print("** class doesn't exist **")

    def do_destroy(self, line):
        """Delete an instance based on the class name and id.
        Usage: destroy <class name> <id>
        """
        args = line.split()
        if len(args) == 0:
            print("** class name missing **")
            return
        try:
            cls = eval(args[0])
            if not issubclass(cls, BaseModel):
                print("** class doesn't exist **")
                return
            if len(args) == 1:
                print("** instance id missing **")
                return
            instance_id = args[1]
            key = "{}.{}".format(class_name, instance_id)
            if key in storage.all():
                del storage.all()[key]
                storage.save()
            else:
                print("** no instance found **")
        except Exception as e:
            print("** class doesn't exist **")

    def do_all(self, line):
        """Print all string representation of all instances, or all instances of a specific class.
        Usage: all [class name]
        """
        if line:
            try:
                cls = eval(line)
                if not issubclass(cls, BaseModel):
                    print("** class doesn't exist **")
                    return
                instances = [str(obj) for key, obj in storage.all().items() if isinstance(obj, cls)]
            except Exception as e:
                print("** class doesn't exist **")
                return
        else:
            instances = [str(obj) for obj in storage.all().values()]
        print(instances)

    def do_update(self, line):
        """Update an instance based on the class name and id by adding or updating an attribute.
    Usage: update <class name> <id> <attribute name> "<attribute value>"
    """
    args = line.split(' ', 3)
    if len(args) < 3:
        if len(args) < 1:
            print("** class name missing **")
        elif len(args) < 2:
            print("** instance id missing **")
        elif len(args) < 3:
            print("** attribute name missing **")
        elif len(args) < 4:
            print("** value missing **")
        return
    
    class_name = args[0]
    instance_id = args[1]
    attribute_name = args[2]
    
    if len(args) < 4:
        print("** value missing **")
    
    try:
        cls = eval(class_name)
        if not issubclass(cls, BaseModel):
            print("** class doesn't exist **")
        
        key = "{}.{}".format(class_name, instance_id)
        instance = storage.all().get(key)
        if instance is None:
            print("** no instance found **")
        
        value = args[3].strip('"')
        
        if hasattr(instance, attribute_name):
            attr_type = type(getattr(instance, attribute_name))
            setattr(instance, attribute_name, attr_type(value))
            instance.save()
        else:
            print("** attribute name missing **")
    
    except Exception as e:
        print("** class doesn't exist **")


if __name__ == '__main__':
    HBNBCommand().cmdloop()

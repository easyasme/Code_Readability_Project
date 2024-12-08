import os
import sys
from re import split


def duplicate_file(file, num=1, *args):
    new_name = None
    print("============")
    if len(sys.argv) == 3 and sys.argv[2].isdigit():
        num = int(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[2].isdigit():
        num = int(sys.argv[2])
        new_name = str(sys.argv[3])
    elif len(sys.argv) == 3 and not sys.argv[2].isdigit():
        new_name = str(sys.argv[2])

    file_name_split = split("-|\.", file)
    old_file_num = int(file_name_split[0])
    name = file_name_split[1]
    file_type = file_name_split[2]

    new_file_num = num + old_file_num
    file_name_split[0] = new_file_num
    if new_name is not None:
        name = new_name

    new_file_name = f"{new_file_num}-{name}.{file_type}"

    if not os.path.isfile(file):
        print(f"{file} does not exist.")
        print("============")
        return
    elif os.path.isfile(new_file_name):
        print(f"{new_file_name} already exists.")
        print("============")
        return
    else:
        print(f"You're creating {new_file_name} from {file}.")
        with open(file, "r") as file_a:
            content = file_a.read()
        with open(new_file_name, "w") as new_file:
            new_file.write(content)
    print("============")


if __name__ == "__main__":
    duplicate_file(sys.argv[1], num=1)

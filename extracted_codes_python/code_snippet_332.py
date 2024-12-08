#!/usr/bin/env python

import time
import pathlib
import os.path
import inspect

from modules.sqlite import execute_db, get_cursor, get_res
from modules.parse_args import parse_arguments

src_file_path = inspect.getfile(lambda: None)
DB = os.path.dirname(src_file_path) + "/test.db"
# print(f"Using: {DB}")


def main():
    args = parse_arguments()

    if args.subcommand == "setup":
        setup_db()
    elif args.subcommand == "add":
        add_path(args.path, args.label, args.alias)
    elif args.subcommand == "rm":
        remove_path(args.path_id, args.type)
    elif args.subcommand == "view":
        view_all_paths(args.showid)
    elif args.subcommand == "alias":
        alias(args.path)
    else:
        raise ValueError(f"Unknown subcommand: {args.subcommand}")


def alias(out_path: str):
    # res = execute_db(DB, "SELECT * FROM path")
    results = get_res(DB, "SELECT alias, path FROM path")
    nbr = 0
    with open(out_path, "w") as out_fh:
        for res in results:
            (alias, path) = res
            if alias is not None:
                nbr += 1
                print(f'alias {alias}="cd {path}"', file=out_fh)
    print(f"{nbr} aliases written to {out_path}")


def setup_db():
    execute_db(DB, "CREATE TABLE path(id, label, path)")
    print(f"New db created in {DB}")


def remove_path(path_id: str, rm_type: "id|path|label" = "id"):
    print("Warning / FIXME: Removing broadly")
    c1 = execute_db(DB, f"DELETE FROM path WHERE id='{path_id}'")
    c2 = execute_db(DB, f"DELETE FROM path WHERE path='{path_id}'")
    c3 = execute_db(DB, f"DELETE FROM path WHERE label='{path_id}'")
    rm_count = c1 + c2 + c3
    print("rm count", rm_count)
    # print(c1, c2, c3)


# https://docs.python.org/3/library/sqlite3.html
def add_path(path: str, label: str, alias: str):
    my_id = time.time_ns()
    execute_db(
        DB, f"INSERT INTO path VALUES ('{my_id}', '{label}', '{path}', '{alias}')"
    )


def view_all_paths(show_id: bool = False):
    con = get_cursor(DB)
    res = con.execute("SELECT * FROM path")

    header = ["path", "label", "alias"]
    rows = list(res.fetchall())
    if show_id:
        header = ["id"] + header
    else:
        rows = [row[1:] for row in rows]

    max_lengths = [0] * len(rows[0])

    for row in rows:
        for i, val in enumerate(row):
            cur_max = max_lengths[i]
            if len(val) > cur_max:
                max_lengths[i] = len(val)

    format_template = "\t".join("{:<" + str(max_len) + "}" for max_len in max_lengths)

    print(format_template.format(*header))
    divider = "-" * (sum(max_lengths) + len("".join(header)) + 1)
    print(divider)
    for row in rows:
        print(format_template.format(*row))


if __name__ == "__main__":
    main()

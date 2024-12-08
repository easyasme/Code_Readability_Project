#!/usr/bin/env python
#
# Copyright (c) 2011-2015 Bertrand Janin <b@janin.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import re
import sys
import argparse

import cartman.app
import cartman.exceptions


def main():
    application = cartman.app.CartmanApp()

    parser = argparse.ArgumentParser(prog="cm")
    parser.add_argument("command",
                        help="required (try help)")
    parser.add_argument("parameters", nargs="*",
                        help="specific for each commands")
    parser.add_argument("-c", dest="add_comment", action="store_true",
                        help="add a comment via the editor (status)")
    parser.add_argument("-m", dest="message", action="store",
                        help="comment/message to be added (status, comment)")
    parser.add_argument("-i", dest="stdin_id", action="store_true",
                        help="grab ticket_id from stdin")
    parser.add_argument("--message-file", action="store",
                        help="read message from file/stdin, disable editor")
    parser.add_argument("-a", dest="open_after", action="store_true",
                        help="open ticket in browser after command")
    parser.add_argument("-s", dest="site", action="store",
                        help="what site to use (default: trac)")
    parser.add_argument("-t", dest="template", action="store",
                        help="template to use for new tickets")
    args = parser.parse_args()

    # Try to grab the ticket id from stdin, if successful, slap the value as an
    # extra positional argument.
    if args.stdin_id:
        data = sys.stdin.read()
        m = re.match(".*#(\d+).*", data, flags=(re.MULTILINE|re.DOTALL))
        if not m:
            raise cartman.exceptions.UsageException("No id on stdin")

        args.append(m.group(1))

    try:
        application.run(args)
    except cartman.exceptions.UsageException as ex:
        sys.stderr.write("{}: {}\n\n".format(ex.prefix, ex))
        parser.print_help(file=sys.stderr)
    except cartman.exceptions.FatalError as ex:
        sys.stderr.write("{}: {}\n".format(ex.prefix, ex))
        sys.exit(1)

if __name__ == '__main__':
    main()

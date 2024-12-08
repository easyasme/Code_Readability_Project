#!/usr/bin/python3

"""
'Re 2+2' computes 2+2 in R :P

# ############################################################################ #
#                                                                              #
#   Copyleft (C) 2020-2023, Marek Gagolewski <https://www.gagolewski.com>      #
#                                                                              #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU Affero General Public License                #
#   Version 3, 19 November 2007, published by the Free Software Foundation.    #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the               #
#   GNU Affero General Public License Version 3 for more details.              #
#   You should have received a copy of the License along with this program.    #
#   If this is not the case, refer to <https://www.gnu.org/licenses/>.         #
#                                                                              #
# ############################################################################ #
"""


import sys
import os, os.path, subprocess
#import qtpy
#from qtpy import QtWidgets
#from qtpy import QtCore
#from qtpy import QtGui
#from qtpy import QtNetwork
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run commands in R.',
        epilog='Copyleft (C) 2020-2023, Marek Gagolewski <https://www.gagolewski.com>',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("cmd", type=str, help="Command to execute.", nargs="+")
    args = parser.parse_args()

    cmds = ";\n".join(args.cmd)


    if os.isatty(0):
        subprocess.run(args=["Rscript", "-e", cmds])
    else:
        subprocess.run(args=["konsole", "--noclose", "-e", "Rscript", "-e", cmds])

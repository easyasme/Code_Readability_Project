#!/usr/bin/env python
#    Copyright (C) 2012 Mark Burnett
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging.config

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str,
            help='YAML file describing measurements to make')
    parser.add_argument('--config', type=str, default='cs.ini',
            help='Logging configuration.')

    return parser.parse_args()

def setup_logging(filename):
    logging.config.fileConfig(filename)

def main(filename):
    logging.info('Starting main.')
    logging.info('Ending main.')

if '__main__' == __name__:
    args = parse_args()
    setup_logging(args.config)
    main(args.filename)

#!/usr/bin/python3
import numpy as np
import argparse
import sys

def dihedral(p):
    """Praxeolitic formula
    1 sqrt, 1 cross product"""
    p0 = p[0]
    p1 = p[1]
    p2 = p[2]
    p3 = p[3]
    b0 = -1.0*(p1 - p0)
    b1 = p2 - p1
    b2 = p3 - p2
    b1 /= np.linalg.norm(b1)
    v = b0 - np.dot(b0, b1)*b1
    w = b2 - np.dot(b2, b1)*b1
    x = np.dot(v, w)
    y = np.dot(np.cross(b1, v), w)
    return np.degrees(np.arctan2(y, x))

def parse_arguments():
    #Parse args
    parser = argparse.ArgumentParser(prog='dh',
                                     description='Get dihedral')
    parser.add_argument('atoms', type=int, nargs=4,
                        help='''4 atoms of the dihedral. Atoms start from 0!''')
    args = parser.parse_args()
    if sys.stdin.isatty():
        raise Exception('Please provide .xyz file to stdin')
    else:
        args.xyzfile = [x[2:-2].split() for x in sys.stdin.readlines()][2:]
    try:
        args.f = args.xyzfile[args.atoms[0]]
        args.s = args.xyzfile[args.atoms[1]]
        args.t = args.xyzfile[args.atoms[2]]
        args.four = args.xyzfile[args.atoms[3]]
    except IndexError:
        print('Your atom numbers are wrong!')
        raise
    return args


if __name__ == '__main__':
    args = parse_arguments()
    p1 = np.array([float(x) for x in args.f]) # CA
    p2 = np.array([float(x) for x in args.s]) # CA
    p3 = np.array([float(x) for x in args.t]) # CA
    p4 = np.array([float(x) for x in args.four]) # CA
    print(dihedral(np.array([p1, p2, p3, p4])))


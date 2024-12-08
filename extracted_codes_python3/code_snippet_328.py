#!/usr/bin/env python3

"""
zfs helper tool
"""

import filecmp
import os
import subprocess
import argparse
from operator import itemgetter
from datetime import datetime


def snapshots(cmd):
    res = []
    rpath = os.path.realpath(cmd.path)
    dataset, mount_path = zfs_dataset_for(rpath)
    rest_path = rpath[len(mount_path):]
    res.append("Mount-path: %s" % colorize(
        mount_path, color='magenta'))
    res.append("Path: %s" % colorize(rpath, color='magenta'))
    res.append("Dataset: %s" % colorize(dataset, color='cyan'))
    res.append("Snapshots:")
    snaps = zfs_snapshots_for(dataset, mount_path, rest_path)
    res += snaps_repr(cmd, rpath, snaps)
    return '\n'.join(res)


def snaps_repr(cmd, rpath, snaps):
    res = []
    for sn in snaps:
        diff = 'same'
        diff_color = 'green'
        if differs(rpath, sn.get('snapshot_path')):
            diff = 'diff'
            diff_color = 'red'
        res.append("%s - %s - %s - %s" % (
            colorize('% 3d' % sn.get('sid'), color='cyan'),
            colorize(diff, color=diff_color),
            colorize(sn.get('creation'), color=diff_color),
            colorize(sn.get('snapshot'), color=diff_color)))

        if cmd.verbose:
            res.append("(%s)" % colorize(
                sn.get('snapshot_path'), color='yellow'))
    if cmd.diffwith:
        res += snap_diff_repr(cmd, rpath, snaps)
    return res


def snap_diff_repr(cmd, rpath, snaps):
    res = []
    snaps_dict = {str(item.get('sid')): item for item in snaps}
    snap_diff = snaps_dict.get(cmd.diffwith)
    if not snap_diff or not snap_diff.get('snapshot_path'):
        res.append("Couldn't diff with %s" % cmd.diffwith)
    else:
        res.append("Diff with snapshot number: %s" % cmd.diffwith)
        res.append("Snapshot: %s" % colorize(
            snap_diff.get('snapshot'), color='red'))
        res.append("Snappath: %s" % colorize(
            snap_diff.get('snapshot_path'), color='yellow'))

        res.append(diff_path(rpath, snap_diff.get('snapshot_path')))
    return res


def zfs_property_for(dataset, prop='all'):
    props = zfs_properties_for(dataset, prop)
    if props and len(props) > 0:
        return props[0].get('value')
    return None


def zfs_properties_for(dataset, prop='all'):
    res = []
    rw = subprocess.check_output(
        ['/sbin/zfs', 'get', '-H', prop, dataset],
        universal_newlines=True)
    for prop in rw.split('\n'):
        pe = prop.split('\t')
        if pe and len(pe) >= 3:
            p = {'snapshot': pe[0],
                 'property': pe[1],
                 'value': pe[2]}
        res.append(p)
    return res


def zfs_snapshots_for(dataset, mount_path, rest_path):
    res = []
    for sn in zfs_snapshots():
        if sn.startswith(dataset):
            snapshot = {}
            snapshot['creation'] = parse_date(
                zfs_property_for(sn, prop='creation'))
            snapshot['snapshot'] = sn
            snapshot['snapshot_mount_path'] = "%s/.zfs/snapshot/%s" % (
                mount_path,
                sn.split('@')[1])
            snapshot['snapshot_path'] = "%s%s" % (
                snapshot.get('snapshot_mount_path'),
                rest_path)
            if os.path.exists(snapshot.get('snapshot_path')):
                res.append(snapshot)
    res = sorted(res, key=itemgetter('creation'), reverse=True)
    counter = 0
    for sn in res:
        sn['sid'] = counter
        counter += 1
    return res


def zfs_dataset_for(fpath):
    ds = zfs_datasets()
    absdir = os.path.dirname(fpath)
    res = ds.get(absdir)
    if not res:
        ldirs = sorted(ds.keys(), key=len, reverse=True)
        for dsp in ldirs:
            if absdir.startswith(dsp):
                return ds.get(dsp), dsp
    return res, absdir


def zfs_datasets():
    res = {}
    rw = subprocess.check_output(
        ['/sbin/zfs', 'mount'],
        universal_newlines=True)
    for ds in rw.split('\n'):
        el = ds.split()
        if len(el) == 2:
            res[el[1]] = el[0]
    return res


def zfs_snapshots():
    res = []
    rw = subprocess.check_output(
        ['/sbin/zfs', 'list', '-t', 'snapshot', '-H'],
        universal_newlines=True)
    for ds in rw.split('\n'):
        el = ds.split()
        if len(el) > 0:
            res.append(el[0])
    return res


def differs(path1, path2):
    if os.path.isfile(path1):
        return not filecmp.cmp(path1, path2)
    return filecmp.dircmp(path1, path2).diff_files


def diff_path(path1, path2):
    diff_cmd = os.environ.get('DIFF', '/usr/bin/diff')
    if os.path.isdir(path1):
        return diff_dirs(diff_cmd, path1, path2)
    else:
        return diff_files(diff_cmd, path1, path2)


def diff_dirs(diff_cmd, path1, path2):
    if diff_cmd.endswith('/diff'):
        cmd = [diff_cmd, '-q', path1, path2]
    else:
        cmd = [diff_cmd, path1, path2]
    dproc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    grep_cmd = ['/usr/bin/grep', '-vi', 'common']
    gproc = subprocess.Popen(
        grep_cmd, stdin=dproc.stdout, stdout=subprocess.PIPE)
    return gproc.stdout.read().decode('utf-8')


def diff_files(diff_cmd, path1, path2):
    cmd = [diff_cmd, path1, path2]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    return proc.stdout.read().decode('utf-8')


def parse_date(dt_str):
    return datetime.strptime(dt_str, "%a %b %d %H:%M %Y")


def colorize(text, effect='1', color='blue'):
    color_codes = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
    }
    return '\033[%s;0;%sm%s\033[0m' % (effect, color_codes.get(color), text)


command_mapping = {
    'snaps': snapshots,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ZFS Info')
    parser.add_argument('-v', '--verbose', help="Verbose output",
                        dest='verbose', action='store_true')
    parser.add_argument('command',
                        choices=command_mapping.keys())
    parser.add_argument('path')
    parser.add_argument('-d', '--diff',
                        dest="diffwith",
                        help="Diff with snap number, customize with $DIFF env",
                        default=None)
    cmd_args = parser.parse_args()
    print(command_mapping[cmd_args.command](cmd_args))

#!/usr/bin/env python
import os
import sys
import platform
import json

URLS = ["https://storage.mds.yandex.net/get-devtools-opensource/250854/aa2abfbb5925abc3609b9d0d14b7da0e"]
MD5 = "aa2abfbb5925abc3609b9d0d14b7da0e"

RETRIES = 5
HASH_PREFIX = 10

HOME_DIR = os.path.expanduser('~')


def create_dirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        import errno

        if e.errno != errno.EEXIST:
            raise

    return path


def misc_root():
    return create_dirs(os.getenv('YA_CACHE_DIR') or os.path.join(HOME_DIR, '.ya'))


def tool_root():
    return create_dirs(os.getenv('YA_CACHE_DIR_TOOLS') or os.path.join(misc_root(), 'tools'))


TOOLS_DIR = tool_root()


def uniq(size=6):
    import string
    import random

    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))


def _fetch(url, into):
    import hashlib

    try:
        import urllib2
        conn = urllib2.urlopen(url, timeout=10)
    except ImportError:
        import urllib.request
        conn = urllib.request.urlopen(url, timeout=10)

    md5 = hashlib.md5()

    sys.stderr.write('Downloading %s [' % (url,))
    try:
        with open(into, "wb") as f:
            while True:
                block = conn.read(1024 * 1024)
                sys.stderr.write('.')
                if block:
                    md5.update(block)
                    f.write(block)
                else:
                    break
        return md5.hexdigest()

    finally:
        sys.stderr.write('] ')


def _atomic_fetch(url, into, md5):
    tmp_dest = into + '.' + uniq()
    try:
        real_md5 = _fetch(url, tmp_dest)
        if real_md5 != md5:
            raise Exception('MD5 mismatched: %s differs from %s' % (real_md5, md5))
        os.rename(tmp_dest, into)
        sys.stderr.write('OK\n')
    except Exception as e:
        sys.stderr.write('ERROR: ' + str(e) + '\n')
        raise
    finally:
        try:
            os.remove(tmp_dest)
        except OSError:
            pass


def _extract(path, into):
    import tarfile

    tar = tarfile.open(path)
    tar.extractall(path=into)
    tar.close()


def _get(urls, md5):
    dest_path = os.path.join(TOOLS_DIR, md5[:HASH_PREFIX])

    if not os.path.exists(dest_path):
        for iter in range(RETRIES):
            try:
                _atomic_fetch(urls[iter % len(urls)], dest_path, md5)
                break
            except Exception:
                if iter + 1 == RETRIES:
                    raise
                else:
                    import time
                    time.sleep(iter)

    return dest_path


def _get_dir(urls, md5):
    packed_path = _get(urls, md5)
    dest_dir = os.path.join(TOOLS_DIR, md5[:HASH_PREFIX] + '_d')

    if os.path.exists(dest_dir):
        return dest_dir

    tmp_dir = dest_dir + '.' + uniq()
    try:
        _extract(packed_path, tmp_dir)

        try:
            os.rename(tmp_dir, dest_dir)
        except OSError as e:
            import errno
            if e.errno != errno.ENOTEMPTY:
                raise

        return dest_dir
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _mine_arc_root():
    return os.path.dirname(os.path.realpath(__file__))


def main():
    if not os.path.exists(TOOLS_DIR):
        os.makedirs(TOOLS_DIR)

    with open(_get(URLS, MD5), 'r') as fp:
        meta = json.load(fp)['data']
    my_platform = platform.system().lower()

    # match by max prefix length
    best_key = max(meta.keys(), key=lambda x: len(os.path.commonprefix([my_platform, x])))
    value = meta[best_key]

    ya_name = {'win32': 'ya-bin.exe'}.get(my_platform, 'ya-bin')  # XXX
    ya_dir = _get_dir(value['urls'], value['md5'])
    ya_path = os.path.join(ya_dir, ya_name)

    env = os.environ.copy()
    src_root = _mine_arc_root()
    if src_root is not None:
        env['YA_SOURCE_ROOT'] = src_root

    if os.name == 'nt':
        import subprocess

        p = subprocess.Popen([ya_path] + sys.argv[1:], env=env)
        p.wait()
        sys.exit(p.returncode)
    else:
        os.execve(ya_path, [ya_path] + sys.argv[1:], env)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.stderr.write('ERROR: ' + str(e) + '\n')
        sys.exit(1)

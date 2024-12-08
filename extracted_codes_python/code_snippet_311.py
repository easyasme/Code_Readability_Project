"""
db.py

Main functions for daybreak.
"""
import toolz
from toolz import curry
from sys import getsizeof
from collections import defaultdict
from journal import Journal
from format import DefaultFormat


class DB(object):

    def __init__(self, file_name='', formatter=None):
        self.file_name = file_name
        self._data = defaultdict(lambda: None)
        if formatter is None:
            formatter = DefaultFormat()
        self._journal = Journal(file_name, formatter)
        self.load()

    def file(self):
        """Returns database file name."""
        return self.file_name

    def default(self, value=None):
        """Set a new default value for database."""
        self._data.default_factory = lambda: value

    def __getitem__(self, key):
        """Retrieve a value at key from the database."""
        if key not in self._data:
            self.set(key, self._data.default_factory())
        return self._data[key]
    get = __getitem__

    @curry
    def __setitem__(self, key, value):
        """Set a key in the database to be written at some future date."""
        self._data[key] = value
        self._journal << [key, value]
        return value
    set = __setitem__

    @curry
    def set_flush(self, key, value):
        """Flushes data immediately to disk."""
        return self.set(key, value)

    def __delitem__(self, key):
        """Delete a key from the database."""
        self._journal << [key]
        return self._data.pop(key, None)
    delete = __delitem__

    def delete_flush(self, key):
        """Immediately delete the key on disk."""
        return self.delete(key)

    def update(self, d):
        """Update database with dict (Fast batch update)."""
        [self.set(*x) for x in d.iteritems()]
        return toolz.merge(self._data, d)

    def update_flush(self, d):
        """Update database with dict (Fast batch update)."""
        return self.update(d)

    def has_key(self, key):
        """Does this db have this key?"""
        return key in self._data
    include = has_key
    is_member = has_key

    def has_value(self, value):
        """Does this db have this value?"""
        return value in self._data.values()

    def size(self):
        """Return the number of stored items."""
        return len(self._data.values())

    def bytesize(self):
        """Utility method that will return the size of the database in bytes."""
        return getsizeof(self._data)

    def logsize(self):
        """Counter of how many records are in the journal."""
        return self._journal.count

    def is_empty(self):
        """Return true if database is empty."""
        return bool(self._data)

    def __iter__(self):
        """Iterate over the key, value pairs in the database."""
        return iter(self._data.items())

    def keys(self):
        """Return the keys in the db."""
        return self._data.keys()

    def flush(self):
        """Flush all changes to disk."""
        self.update(self._data)

    def load(self):
        """Sync the database with what is on disk."""
        self._data = defaultdict(self._data.default_factory, dict(self._journal.load()))
    sunrise = load

    def lock(self):
        """Lock the database for an exclusive commit across processes and threads."""
        # TODO: This lock should be a subclass with methods __enter__ and __exit__ so developers can user as:
        #    with db.lock:
        #        pass
        pass

    def synchronize(self):
        """Synchronize access to the database from multiple threads."""
        pass

    def clear(self, flush=False):
        """Remove all keys and values from the database."""
        if flush:
            self._journal.clear()
        return self._data.clear()

    def compact(self):
        """Compact the database to remove stale commits and reduce the file size."""
        self._journal.clear()
        self.flush()

    def close(self):
        """Close the database for reading and writing."""
        self.clear()
        self._journal.close()

    def closed(self):
        """Checks if the database connection has been closed."""
        return self._journal.closed()

    def values(self):
        """Returns a list of the internal dictionary values."""
        return self._data.values()

    def __del__(self):
        """A handler that will ensure that databases are closed and synced when the current process exits."""
        pass

class LRUCache:

    def __init__(self, capacity: int):
        self.n = capacity
        self.cache = {}  # Stores key-value pairs
        self.usage = []  # Tracks usage order of keys

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.usage.remove(key)
        self.usage.append(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.usage.remove(key)
        elif len(self.cache) >= self.n:
            del self.cache[self.usage.pop(0)]
        self.usage.append(key)
        self.cache[key] = value

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Dictionary to store key -> value mapping
        self.order = []  # List to maintain the order of keys

    def get(self, key: int) -> int:
        if key in self.cache:
            # Move the accessed key to the end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update the value and move key to the end
            self.cache[key] = value
            self.order.remove(key)
        else:
            if len(self.cache) >= self.capacity:
                # Remove the least recently used key (first in the list)
                lru = self.order.pop(0)
                del self.cache[lru]
            self.cache[key] = value
        self.order.append(key)
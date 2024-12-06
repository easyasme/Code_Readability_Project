class LRUCache:

    def __init__(self, capacity: int):
        self.cache = {}  # Maps key to value
        self.capacity = capacity
        self.values = {}  # Maps order to key
        self.keys = {}    # Maps key to order
        self.curr = 0     # Tracks the current usage order

    def get(self, key: int) -> int:
        if key in self.cache:
            # Update the access order
            old_order = self.keys[key]
            del self.values[old_order]
            self.values[self.curr] = key
            self.keys[key] = self.curr
            self.curr += 1
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update the existing key's value and order
            self.cache[key] = value
            old_order = self.keys[key]
            del self.values[old_order]
            self.values[self.curr] = key
            self.keys[key] = self.curr
            self.curr += 1
        else:
            if len(self.cache) >= self.capacity:
                # Find and remove the least recently used item
                lru_order = min(self.values.keys())
                lru_key = self.values[lru_order]
                del self.cache[lru_key]
                del self.keys[lru_key]
                del self.values[lru_order]
            
            # Add the new key-value pair
            self.cache[key] = value
            self.values[self.curr] = key
            self.keys[key] = self.curr
            self.curr += 1

        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
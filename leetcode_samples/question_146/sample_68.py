class LRUCache:

    def __init__(self, capacity: int):
        assert capacity > 0
        self.capacity = capacity
        self.cache = {}
        self.stack = []

    def get(self, key: int) -> int:

        try:
            value = self.cache[key]
            self.stack.remove(key)
            self.stack.append(key)
            return value
        
        except KeyError:
            return -1

    def put(self, key: int, value: int) -> None:
        
        if key in self.cache:
            self.stack.remove(key)
        
        elif len(self.cache) >= self.capacity:
            lru = self.stack.pop(0)
            del self.cache[lru]
        
        self.cache[key] = value
        self.stack.append(key)

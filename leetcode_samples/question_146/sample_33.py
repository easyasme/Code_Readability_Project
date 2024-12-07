class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.used_dict = {}

    def get(self, key: int) -> int:
        self.used(key)
        return self.cache.get(key, -1)

    def put(self, key: int, value: int) -> None:
        # check if i am at capacity,
        # if yes remove the last recently used
        if key in self.cache:
            self.cache[key] = value
            self.used(key)
            return
        if len(self.cache) == self.capacity:
            lru = list(self.used_dict.keys())[0]
            del self.cache[lru]
            del self.used_dict[lru]
        self.cache[key] = value
        self.used(key)
        
    def used(self, key) -> None:
        if key not in self.cache:
            return
        if key in self.used_dict:
            del self.used_dict[key]
        self.used_dict[key] = 1
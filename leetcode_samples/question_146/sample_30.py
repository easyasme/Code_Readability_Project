class LRUCache:

    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}


    def get(self, key: int) -> int:
        if key in self.cache:
            val = self.cache[key]
            del self.cache[key]
            self.cache[key] = val
        return self.cache.get(key,-1)        

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            del self.cache[key]
        elif  len(self.cache.keys()) == self.cap:
            lru = list(self.cache.keys())[0]
            del self.cache[lru]
        self.cache[key] = value

        
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
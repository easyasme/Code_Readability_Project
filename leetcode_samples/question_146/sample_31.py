class LRUCache:

    def __init__(self, capacity: int):
        self.cache = {}
        self.capacity = capacity

    def update(self, key, value):
        del self.cache[key]
        self.cache[key] = value
    
    def get(self, key: int) -> int:
        if key in self.cache:
            value = self.cache[key]
            self.update(key, value)
            return value
        else:
            return -1
        
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.update(key, value)
        else:
            self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            LRU_Key = list(self.cache.keys())[0]
            del self.cache[LRU_Key]
        

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
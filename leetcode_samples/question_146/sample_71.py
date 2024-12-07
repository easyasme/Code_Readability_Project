class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.keys = []
        self.values = {}

    def get(self, key: int) -> int:
        if key in self.values:
            self.keys.remove(key)
            self.keys.append(key)
            return self.values[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.values:
            self.keys.remove(key)
        
        if len(self.keys) == self.capacity:
            keyToRemove = self.keys[0]
            del self.keys[0]
            del self.values[keyToRemove]
        
        self.keys.append(key)
        self.values[key] = value



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
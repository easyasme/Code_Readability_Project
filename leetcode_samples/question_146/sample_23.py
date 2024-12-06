from sortedcontainers import SortedSet

class LRUCache:

    def __init__(self, capacity: int):
        self.ss = SortedSet() 
        self.map = {} 
        self.lastUsedAt = {} 
        self.counter = 0 
        self.capacity = capacity 
        
    def get(self, key: int) -> int:
        self.counter -= 1 
        
        if key not in self.map:
            return -1 

        # update last used at 
        # remove last used for key 
        # print(f"removing {self.lastUsedAt[key]}, {key}")
        self.ss.remove((self.lastUsedAt[key], key))
        self.lastUsedAt[key] = self.counter 
        self.ss.add((self.lastUsedAt[key], key))

        return self.map[key]

    def put(self, key: int, value: int) -> None:

        self.counter -= 1 

        if key in self.lastUsedAt:
            # remove old instance 
            self.ss.remove((self.lastUsedAt[key], key))

        self.lastUsedAt[key] = self.counter 
        # add back new instance 
        self.ss.add((self.lastUsedAt[key], key))

        if len(self.ss) > self.capacity:
            evictedKey = self.ss.pop(-1)[1]
            # print(evictedKey, ' evictedKey')
            del self.lastUsedAt[evictedKey] 
            del self.map[evictedKey]
        
        self.map[key] = value 

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
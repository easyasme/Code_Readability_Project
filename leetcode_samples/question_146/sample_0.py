from collections import OrderedDict
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    def get(self, key:int)->int:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            return -1
    def put(self, key, value):
        if key in  self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            self.cache[key] = value
        if len(self.cache)>self.capacity:
            self.cache.popitem(last=False)
cache = LRUCache(2)        # Capacity is 2
cache.put(1, 1)            # Cache is {1=1}
cache.put(2, 2)            # Cache is {1=1, 2=2}
assert cache.get(1) == 1   # Returns 1 and moves 1 to the most recently used position, Cache is {2=2, 1=1}
cache.put(3, 3)            # Evicts key 2, Cache is {1=1, 3=3}
assert cache.get(2) == -1  # Returns -1 (not found)
cache.put(4, 4)            # Evicts key 1, Cache is {3=3, 4=4}
assert cache.get(1) == -1  # Returns -1 (not found)
assert cache.get(3) == 3   # Returns 3
assert cache.get(4) == 4  
        
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.log = {}
        self.t = 1

    
    def get(self, key):
        self.t += 1
        if key in self.cache:
            val, old_t = self.cache[key]
            del self.log[old_t]
            self.log[self.t] = key
            self.cache[key] = [val, self.t]
            return val
        return -1


    def put(self, key, val):
        self.t += 1
        if key in self.cache:
            old_t = self.cache[key][1]
            del self.log[old_t]
            del self.cache[key]
        self.log[self.t] = key
        self.cache[key] = [val, self.t]
        if len(self.cache) > self.capacity:
            self.evict()

    def evict(self):
        min_t = min(self.log)
        min_k = self.log[min_t]
        del self.log[min_t]
        del self.cache[min_k]

    # def __init__(self, capacity: int):
    #     self._capacity = capacity
    #     self._cache = {} # {1: [2, t1], 9:[7: t2], ...}
    #     self._log = {} # {t1: 1, t2: 9, ..}
    #     self._timer = 1 #increment by 1 at each op

    # def get(self, key: int) -> int:
    #     self._timer += 1
    #     if key in self._cache:
    #         prev_time = self._cache[key][1]
    #         del self._log[prev_time]
    #         self._log[self._timer] = key
    #         self._cache[key] = [self._cache[key][0], self._timer]
    #         return self._cache[key][0]
    #     return -1
        

    # def put(self, key: int, value: int) -> None:
    #     self._timer += 1
    #     if key in self._cache:
    #         prev_time = self._cache[key][1]
    #         del self._cache[key]
    #         del self._log[prev_time]
    #     self._cache[key] = [value, self._timer]
    #     self._log[self._timer] = key
    #     if len(self._cache) > self._capacity:
    #         self.evict() # o(1)
    # def evict(self):
    #     lru = min(self._log)
    #     lru_key = self._log[min(self._log)]
    #     del self._log[lru]
    #     del self._cache[lru_key]


    # def __init__(self, capacity):
    #     self.cache = {}
    #     self.t = 0
    #     self.capacity = capacity

    # def get(self, key):
    #     self.t += 1
    #     if key in self.cache:
    #         self.cache[key][1] = self.t
    #         return self.cache[key][0]
    #     return -1

    # def evict(self):
    #     min_t = sys.maxsize
    #     min_k = None
    #     for k in self.cache:
    #         if self.cache[k][1] < min_t:
    #             min_t = self.cache[k][1]
    #             min_k = k
    #     if min_k:
    #         del self.cache[min_k]

    # def put(self, key, value):
    #     self.t += 1
    #     if key in self.cache:
    #         # no need to adjust capacity
    #         self.cache[key] = [value, self.t]
    #         # self.cache[key][1] += self.t
    #     else:

    #         self.cache[key] = [value, self.t]
    #         if len(self.cache) > self.capacity:
    #             self.evict()


















    # def __init__(self, capacity: int):
    #     self._capacity = capacity
    #     self._cache = {} # {1: [2, t1], 9:[7: t2], ...}
    #     self._log = {} # {t1: 1, t2: 9, ..}
    #     self._timer = 1 #increment by 1 at each op

    # def get(self, key: int) -> int:
    #     self._timer += 1
    #     if key in self._cache:
    #         prev_time = self._cache[key][1]
    #         del self._log[prev_time]
    #         self._log[self._timer] = key
    #         self._cache[key] = [self._cache[key][0], self._timer]
    #         return self._cache[key][0]
    #     return -1
        

    # def put(self, key: int, value: int) -> None:
    #     self._timer += 1
    #     if key in self._cache:
    #         prev_time = self._cache[key][1]
    #         del self._cache[key]
    #         del self._log[prev_time]
    #     self._cache[key] = [value, self._timer]
    #     self._log[self._timer] = key
    #     if len(self._cache) > self._capacity:
    #         self.evict() # o(1)
    # def evict(self):
    #     lru = min(self._log)
    #     lru_key = self._log[min(self._log)]
    #     del self._log[lru]
    #     del self._cache[lru_key]
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
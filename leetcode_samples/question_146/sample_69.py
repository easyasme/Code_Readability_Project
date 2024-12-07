class LRUCache:


    def __init__(self, capacity: int):
        self.capacity = capacity
        self.q = []
        self.m = defaultdict(int)
        

    def get(self, key: int) -> int:
        if key in self.m:
            self.q.remove(key)
            self.q.append(key)
            return self.m[key]
        return -1
        

    def put(self, key: int, value: int) -> None:
        if len(self.q) < self.capacity:
            if key in self.m:
                self.get(key)
            else:
                self.q.append(key)
            self.m[key] = value
        else:
            if key in self.m:
                self.get(key)
            else:
                rm = self.q.pop(0)
                del self.m[rm]
                self.q.append(key)
            self.m[key] = value
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.prev, self.next = {}, {}
        self.head, self.tail = "$", "#"
        self.cache = {}
        self.connect(self.head, self.tail)

    def connect(self, prev, next):
        self.prev[next], self.next[prev] = prev, next

    def add(self, k, v):
        if k in self.cache:
            self.delete(k)
        self.cache[k] = v
        self.connect(self.prev[self.tail], k)
        self.connect(k, self.tail)

    def delete(self, k):
        self.connect(self.prev[k], self.next[k])
        del self.cache[k], self.prev[k], self.next[k]
        

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        v = self.cache[key]
        self.delete(key)
        self.add(key, v)
        return v
        

    def put(self, key: int, value: int) -> None:
        if key not in self.cache and len(self.cache) + 1 > self.capacity:
            self.delete(self.next[self.head])
        self.add(key, value)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity: int):
        self.dict = {}
        self.capacity = capacity
        self.access = []

    def get(self, key: int) -> int:
        if key in self.dict:
            self.access.remove(key)
            self.access.append(key)
            return self.dict[key]
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.dict:
            self.dict[key] = value
            self.access.remove(key)
            self.access.append(key)
        else:
            if len(self.dict) < self.capacity:
                self.dict[key] = value
                self.access.append(key)
            else:
                last_access_key = self.access.pop(0)
                del self.dict[last_access_key]
                self.dict[key] = value
                self.access.append(key)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
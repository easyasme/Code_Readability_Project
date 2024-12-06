class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.d = {}
        

    def get(self, key: int) -> int:
        if key not in self.d:
            return -1

        value = self.d[key]
        del self.d[key]
        self.d[key] = value

        return value
        

    def put(self, key: int, value: int) -> None:
        if key in self.d:
            del self.d[key]

        if len(self.d.keys()) < self.capacity:
            self.d[key] = value
        else:
            # delete the first key-value
            first_key = list(self.d.keys())[0]
            del self.d[first_key]

            # add key-value
            self.d[key] = value

        return
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
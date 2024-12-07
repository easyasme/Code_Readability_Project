class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dict = {}
        

    def get(self, key: int) -> int:
        if key in self.dict.keys():
            val = self.dict[key]
            del self.dict[key]
            self.dict[key] = val
            return val
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.dict.keys():
            del self.dict[key]
            self.dict[key] = value
        else:
            if len(self.dict) < self.capacity:
                self.dict[key] = value
            else:
                del self.dict[list(self.dict)[0]]
                self.dict[key] = value   

        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
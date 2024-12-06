class LRUCache:

    def __init__(self, capacity: int):
        self._dict = {}
        self.capacity = capacity

    def get(self, key: int) -> int:

        if key in self._dict.keys():
            used_key, used_value = key, self._dict[key]
            del self._dict[used_key]
            self._dict[used_key] = used_value
            return self._dict[used_key]
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key not in self._dict.keys():
            if len(self._dict.items()) >= self.capacity:
                del self._dict[list(self._dict.keys())[0]]
            self._dict[key] = value
            
        else:
            del self._dict[key]
            self._dict[key] = value
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
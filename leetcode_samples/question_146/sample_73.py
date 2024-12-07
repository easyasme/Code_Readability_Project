class LRUCache:

    def __init__(self, capacity: int):
        self.key_list = list()
        self.key_value = dict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key in self.key_value:
            self.key_list.remove(key)
            self.key_list.append(key)
            return self.key_value[key]
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.key_value:
            self.key_list.remove(key)
            self.key_list.append(key)
            self.key_value[key] = value
        else:
            self.key_value[key] = value
            if len(self.key_list) >= self.capacity:
                rm = self.key_list.pop(0)
                self.key_value.pop(rm)
            self.key_list.append(key)
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.op_num_to_key = {}
        self.key_to_op_num = {}
        self.op_num = 0

    def get(self, key: int) -> int:
        if key in self.cache:
            self.op_num_to_key[self.op_num] = key
            self.key_to_op_num[key] = self.op_num
            self.op_num+=1
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
     #   print(self.key_to_op_num)
        if key in self.cache:
            self.op_num_to_key[self.op_num] = key
            self.key_to_op_num[key] = self.op_num
        else:
            if len(self.cache) == self.capacity:
                old_key = self.op_num_to_key[min(self.key_to_op_num.values())]
                del self.key_to_op_num[old_key]
                del self.cache[old_key]
            self.op_num_to_key[self.op_num] = key
            self.key_to_op_num[key] = self.op_num
        self.cache[key] = value
        self.op_num+=1
    #    print(self.cache)



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dic = {}
        self.count = 0 
        # self.recent = None 
        self.stack = [] 

    def get(self, key: int) -> int:
        if key in self.dic:
            self.stack.remove(key)
            self.stack.append(key)
            return self.dic[key]
        return -1 

    def put(self, key: int, value: int) -> None:
        if key in self.dic: 
            self.dic[key] = value 
            self.stack.remove(key)
            self.stack.append(key)
        else:
            if self.count == self.capacity: 
            # print(self.stack)
                del self.dic[self.stack.pop(0)]
                self.count -= 1 
            self.dic[key] = value       
            self.stack.append(key)
            self.count += 1 

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
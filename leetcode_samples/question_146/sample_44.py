import collections
import time
class LRUCache:

    def __init__(self, capacity: int):
        self.capacity=capacity
        self.dict=collections.OrderedDict()

    def get(self, key: int) -> int:
        time.sleep(0.000005)
        if key not in self.dict:
            return -1
        self.dict.move_to_end(key)
        return self.dict[key]

    def put(self, key: int, value: int) -> None:
        if key in self.dict:
            self.dict.move_to_end(key)
        self.dict[key]=value
        if len(self.dict)>self.capacity:
            self.dict.popitem(False)


        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
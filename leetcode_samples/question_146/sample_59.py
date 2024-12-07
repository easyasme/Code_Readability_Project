class LRUCache: #7:54pm - 

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.counter = 1
        self.dict = {}
        self.counterDict = {}
        

    def get(self, key: int) -> int:
        if key in self.dict:
            self.put(key, self.dict[key]['value'])
            return self.dict[key]['value']
        return -1
        

    def put(self, key: int, value: int) -> None:
        if key in self.dict:
            # update value. update key as something recently used
            oldCounter = self.dict[key]['count']
            self.counterDict.pop(oldCounter)
            self.dict[key] = {'value': value, 'count': self.counter}
            self.counterDict[self.counter] = key
            self.counter += 1
        elif len(self.dict) < self.capacity:
            self.dict[key] = {'value': value, 'count': self.counter}
            self.counterDict[self.counter] = key
            self.counter += 1
        else: # len of self.dict == capacity
            # find least recently used, counter - capacity (11-10)
            oldestCount = min(self.counterDict)
            oldestKey = self.counterDict[oldestCount]
            self.counterDict.pop(oldestCount)
            self.dict.pop(oldestKey)
            self.put(key, value)


        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
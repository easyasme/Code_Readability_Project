

class LRUCache:

    def __init__(self, capacity: int):
        self.map = {}
        self.counts = {}
        self.queue = []
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key in self.map:
            self.queue.append(key)
            self.counts[key] += 1
            return self.map[key]
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self.map[key] = value
            self.counts[key] += 1
            self.queue.append(key)
        else:
            self.map[key] = value
            self.counts[key] = 1
            self.queue.append(key)
            if len(self.map) > self.capacity:
                while self.queue:
                    curcheck = self.queue[0]
                    self.queue = self.queue[1:]
                    self.counts[curcheck] -= 1
                    if self.counts[curcheck] == 0:
                        del self.map[curcheck]
                        break

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:
    """LRU Cache object"""
    def __init__(self, capacity: int):
        """instantiate LRU cache"""
        self.capacity = capacity
        self.min_heap = []
        self.tracker = {}
        self.counter = itertools.count()

    def get(self, key: int) -> int:
        """gets the value of a key"""
        try:
            value = self.tracker[key][1]
            self.tracker[key] = (next(self.counter), value)
            heapq.heappush(self.min_heap, (self.tracker[key][0], key))
            return value
        except KeyError:
            return -1

    def put(self, key: int, value: int):
        if key not in self.tracker and len(list(self.tracker.keys())) + 1 > self.capacity:
            recency_index, heap_key = heapq.heappop(self.min_heap)

            while self.tracker[heap_key][0] != recency_index:
                recency_index, heap_key = heapq.heappop(self.min_heap)

            self.tracker.pop(heap_key)
            
        self.tracker[key] = (next(self.counter), value)
        heapq.heappush(self.min_heap, (self.tracker[key][0], key))
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
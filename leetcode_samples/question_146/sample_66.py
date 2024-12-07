class LRUCache:
    '''
    naive:
    use a dict to store {key: val}
    use a list to store lru
    time: O(n) for get, put
    space: O(n)
    '''

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = defaultdict(int)
        self.lru = []  # tail is most recently used

    def get(self, key: int) -> int:
        if key in self.cache:
            self.lru.remove(key)
            self.lru.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.lru.remove(key)
            self.lru.append(key)
        else:
            self.lru.append(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            evict = self.lru.pop(0)
            self.cache.pop(evict)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
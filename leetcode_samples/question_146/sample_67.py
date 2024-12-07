class LRUCache:
    # LRU cache will be backed by a key-value lookup DS (ex. dict)
    # order will be maintained by a 2nd DS (ex. queue)
    # on get/put of existing key, need to remove from current position in queue and place in the back
    # on put of new key where we exceed capacity, pop from queue and remove from KV store

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dict = {}
        self.queue = []

    def get(self, key: int) -> int:
        if key not in self.dict:
            return -1
        cache_item = self.dict[key]
        self.__update_existing_key_usage(cache_item)
        return cache_item.value

    def put(self, key: int, value: int) -> None:
        if key in self.dict:
            cache_item = self.dict[key]
            cache_item.value = value
            self.__update_existing_key_usage(cache_item)
        else:
            cache_item = LRUCacheItem(key, value)
            self.dict[key] = cache_item
            self.queue.append(cache_item)
        if len(self.dict) > self.capacity:
            # evict the LRU key
            evicted_cache_item = self.queue.pop(0)
            del self.dict[evicted_cache_item.key]
    
    def __update_existing_key_usage(self, cache_item):
        self.queue.remove(cache_item)
        self.queue.append(cache_item)

class LRUCacheItem:
    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
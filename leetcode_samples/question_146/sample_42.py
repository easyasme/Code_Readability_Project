class ListNode:
    def __init__(self, data):
        self.data = data
        self.previous = None
        self.next = None

class LRUCache:

    hash_value = 100007

    def __init__(self, capacity: int):
        self.cap = capacity
        self.curr_cap = 0
        self.keys = [[] for _ in range(self.hash_value)]
        self.values = [[] for _ in range(self.hash_value)]
        
        self.head, self.tail = ListNode(-1), ListNode(-1)
        self.head.next = self.tail
        self.tail.previous = self.head

    def __hash(self, key):
        return key % self.hash_value

    def __update_lru_cache(self, node):
        # we cannot update the latest used node or if there's only a single node in the cache
        if node.next != self.tail:
            left, right = node.previous, node.next
            left.next, right.previous = right, left
            # place the node just before the tail
            mru_node = self.tail.previous
            node.previous, mru_node.next = mru_node, node
            node.next, self.tail.previous = self.tail, node
    
    def __add_to_lru_cache(self, node):
        if self.curr_cap + 1 > self.cap:
            # we're over the cache storage limit
            # remove the Least-Recently-Used key-val pair
            lru_node = self.head.next
            self.__remove_from_key_val_store(lru_node.data)
            new_lru_node = lru_node.next
            new_lru_node.previous = self.head
            self.head.next = new_lru_node
            lru_node.next = lru_node.previous = None
            del lru_node
            self.curr_cap -= 1
        # add just before the tail which represents Most-Recently-Used key
        mru_node = self.tail.previous
        mru_node.next, node.previous = node, mru_node
        self.tail.previous, node.next = node, self.tail
        self.curr_cap += 1
    
    def __remove_from_key_val_store(self, key):
        bucket_idx = self.__hash(key)
        key_idx = self.keys[bucket_idx].index(key)
        del self.keys[bucket_idx][key_idx]
        del self.values[bucket_idx][key_idx]

    def get(self, key: int) -> int:
        bucket_idx = self.__hash(key)
        if key not in self.keys[bucket_idx]:
            return -1
        key_idx = self.keys[bucket_idx].index(key)
        val, node = self.values[bucket_idx][key_idx]
        self.__update_lru_cache(node)   # mark the current node as most-recently-used key
        return val

    def put(self, key: int, value: int) -> None:
        bucket_idx = self.__hash(key)
        if key in self.keys[bucket_idx]:    # update
            key_idx = self.keys[bucket_idx].index(key)
            _, node = self.values[bucket_idx][key_idx]
            self.__update_lru_cache(node)
            self.values[bucket_idx][key_idx] = (value, node)
        else:
            self.keys[bucket_idx].append(key)
            node = ListNode(key)
            self.values[bucket_idx].append((value, node))
            self.__add_to_lru_cache(node)

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
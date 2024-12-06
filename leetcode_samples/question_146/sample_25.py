
"""
update lru at get
update lru at put
validate capacity every put
"""

class Node:

    def __init__(self):
        self.next = None
        self.prev = None
        self.key = None
        self.val = None

class LRUCache:

    def __init__(self, capacity: int):
        self.items = dict()
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.capacity = capacity

    def get(self, key: int) -> int:
        print('get', key)

        if key in self.items:
            node = self.items[key]
            val = node.val
            print('get', key, val)
            self._remove(key)
            self._add(key, val)
            return self.items[key].val
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        print('put', key, value)

        if key in self.items:
            self._remove(key)

        self._add(key, value)
        
        # handle capacity
        if len(self.items) > self.capacity:
            self._remove(self.tail.prev.key)

    def _add(self, key, val):

        print('add', key, val)

        node = Node()
        node.val = val
        node.key = key

        head = self.head
        head_next = self.head.next

        head.next = node
        head_next.prev = node

        node.prev = head
        node.next = head_next

        self.items[key] = node

    def _remove(self, key):
        print('remove',key)
        node = self.items[key]

        prev_node = node.prev
        next_node = node.next

        prev_node.next = next_node
        next_node.prev = prev_node

        self.items.pop(key)
        
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
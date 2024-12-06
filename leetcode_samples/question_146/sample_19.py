from collections import deque

class Node:
    def __init__(self, k, v, next=None, prev=None):
        self.key = k
        self.val = v
        self.next = next
        self.prev = prev
    
    def __str__(self):
        ptr = self
        while ptr:
            print(ptr.val)
            ptr = ptr.next


class LRUCache:
    def __init__(self, capacity: int):
        self.cache = {}
        self.cap = capacity
        self.head = None
        self.tail = None

    # 1-><-2-><-3-><-4


    def delete_node(self, node):
        if node.prev:
            node.prev.next = node.next
        else: # first node
            self.head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else: # last node
            self.tail = node.prev

    def pop_left(self):
        if not self.head:
            return None
        
        node = self.head
        # single node
        if self.tail == self.head:
            self.tail = None
            self.head = None
            return node
        
        print(self.head.val)
        self.head.next.prev = None
        self.head = self.head.next
        print(self.head.val)
        return node


    def push_right(self, node):
        if not self.tail:
            self.head = self.tail = node
            node.next = None
            return

        node.next = self.tail.next
        self.tail.next = node
        node.prev = self.tail
        self.tail = node


    def move_to_tail(self, node):
        self.delete_node(node)
        self.push_right(node)


    def get(self, key: int) -> int:
        print('get', key)
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self.move_to_tail(node)
        print('head, tail -', self.head.val, self.tail.val)
        return node.val

    def put(self, key: int, value: int) -> None:
        print('put', key, value)

        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self.move_to_tail(node)
            return

        # key not in cache
        node = Node(key, value)
        if len(self.cache) == self.cap:
            print('cache full')
            # evict
            lru_node = self.pop_left()
            del self.cache[lru_node.key]

        self.cache[key] = node
        self.push_right(node)
        print('head, tail -', self.head.val, self.tail.val)



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
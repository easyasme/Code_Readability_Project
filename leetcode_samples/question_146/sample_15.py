class Node:
    def __init__(self, val, key):
        self.val = val
        self.key = key
        self.next, self.prev = None, None

class LRUCache:

    def __init__(self, capacity: int):
        self.positions = dict()
        self.head = Node(-1,-1) # MRU
        self.tail = Node(-1,-1) # LRU
        self.head.next = self.tail
        self.tail.prev = self.head
        self.cap = capacity

    def addMRU(self, node):
        tmp = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = tmp
        tmp.prev = node
    
    def remove(self, node):
        prev, nxt = node.prev, node.next
        print(prev, node.val, nxt)
        prev.next = nxt
        nxt.prev = prev
        node.prev, node.next = None, None

    def get(self, key: int) -> int:
        if key not in self.positions:
            return -1
        node = self.positions[key]
        self.remove(node)
        self.addMRU(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.positions:
            node = self.positions[key]
            node.val = value
            self.remove(node)
            self.addMRU(node)
            return

        node = Node(value, key)
        self.addMRU(node)
        self.positions[key] = node

        if len(self.positions) > self.cap:
            to_remove = self.tail.prev
            self.remove(to_remove)
            self.positions.pop(to_remove.key)



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
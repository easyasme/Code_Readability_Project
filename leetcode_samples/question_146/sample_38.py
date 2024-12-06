class Node:
    def __init__(self, key, value):
        self.value = value
        self.key = key
        self.next = None
        self.prev = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.map = {}
        self.head = Node(None, None)
        self.head.next = self.head
        self.head.prev = self.head
        

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        
        node = self.map[key]
        self._update(node)
    
        return node.value

    def _update(self, node):
        if node.prev and node.next:
            node.prev.next = node.next
            node.next.prev = node.prev

        node.prev = self.head.prev
        node.prev.next = node
        self.head.prev = node
        node.next = self.head
        
    def put(self, key: int, value: int) -> None:
        if key in self.map:
            node = self.map[key]
            node.value = value
        else:
            # print(key, value, self.head.next.value, self.head.prev.value)
            if len(list(self.map.keys())) == self.capacity:
                least_recent = self.head.next
                self.head.next = least_recent.next
                least_recent.next.prev = self.head
                del self.map[least_recent.key]
                del least_recent

            node = Node(key, value)
        self._update(node)
        self.map[key] = node
            

        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
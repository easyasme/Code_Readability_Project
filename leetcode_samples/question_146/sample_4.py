class Node:
    def __init__(self, key,value):
        self.key=key
        self.value=value
        self.next=self.prev=None

# size = 2
# 1 -> 
# 2 -> 1
# 1 -> 2
# 3 -> 1 -> 2 - 2 evicted lru
# 3 -> 1
# 4 -> 3 -> 1 - 1 evicted lru
# 3 -> 4 - 3
# 4 -> 3 - 4

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.size = 0
        self.head, self.tail = Node(0,0), Node(0,0) # self.head -> [0,0], self.tail -> [0,0]
        # placeholders for nodes to easily manipulate new incoming nodes.
        self.head.next = self.tail
        self.tail.prev = self.head

    def insert(self, node):
        node.next = self.head.next
        node.next.prev = node
        self.head.next = node
        node.prev = self.head
    
    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def get(self, key: int) -> int:
        if key not in self.cache: return -1
        node = self.cache[key]
        self.remove(node)
        self.insert(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key not in self.cache:
            if self.size >= self.capacity:
                # evict lru from tail prev
                node_to_remove = self.tail.prev
                self.remove(node_to_remove)
                del self.cache[node_to_remove.key]
                self.size -= 1
            # add new node in cache and in DLL
            node = Node(key, value)
            self.insert(node)
            self.cache[key] = node
            self.size += 1
        else:
            # replace the node with val key
            node = self.cache[key]
            node.value = value
            self.remove(node) # remove and make it go to head, mru
            self.insert(node)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
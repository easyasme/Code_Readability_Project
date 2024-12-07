class Node:
    def __init__(self, val: int):
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.start = Node(0)
        self.end = Node(0)
        self.start.next = self.end
        self.end.prev = self.start
    
    def add_node(self, node: Node) -> None:
        node.prev = self.start
        node.next = self.start.next
        self.start.next.prev = node
        self.start.next = node
    
    def remove_node(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            self.remove_node(node)
            self.add_node(node)
            return node.val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self.remove_node(node)
            self.add_node(node)
        else:
            new_node = Node(value)
            new_node.prev = self.start
            new_node.next = self.start.next
            self.start.next.prev = new_node
            self.start.next = new_node
            self.cache[key] = new_node
            if len(self.cache) > self.capacity:
                for key, node in self.cache.items():
                    if node == self.end.prev:
                        break
                self.remove_node(node)
                del self.cache[key]


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LinkedNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None


class LRUCache:

    def __init__(self, capacity: int):
        self.node_mapper = {}
        self.capacity = capacity 
        self.head = LinkedNode(-1, -1)
        self.tail = LinkedNode(-1, -1)
        self.head.next = self.tail
        self.tail.prev = self.head 

    def get(self, key: int) -> int:
        if key in self.node_mapper:
            node = self.node_mapper[key]
            self.remove(node)
            self.add(node)
            return node.val

        return -1


    def put(self, key: int, value: int) -> None:
        
        if key in self.node_mapper:
            old_node = self.node_mapper[key]
            self.remove(old_node)

        node = LinkedNode(key, value)
        self.node_mapper[key] = node
        self.add(node)

        if len(self.node_mapper) > self.capacity:
            node_to_delete = self.head.next
            self.remove(node_to_delete)
            del self.node_mapper[node_to_delete.key]


    def add(self, node):
        self.tail.prev.next = node
        node.next = self.tail
        node.prev = self.tail.prev
        self.tail.prev = node

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
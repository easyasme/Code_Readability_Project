class ListNode:
    
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None

class LRUCache:
    
    def __init__(self, capacity: int):
        self.map = {}
        self.capacity = capacity
        self.head = ListNode(-1)
        self.tail = ListNode(-1)
        self.head.next = self.tail
        self.tail.prev = self.head
        
    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        
        node = self.map[key]
        self.remove(node)
        self.add(node)
        
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            node = self.map[key]
            node.val = value
            self.remove(node)
            self.add(node)
        else:
            self.map[key] = ListNode(value)
            self.add(self.map[key])
            
            
        if len(self.map) > self.capacity:
            for key, value in self.map.items():
                if value == self.head.next:
                    del self.map[key]
                    break    
            self.remove(self.head.next)
                

    def add(self, node):
        prevNode = self.tail.prev
        node.next = self.tail
        self.tail.prev = node
        node.prev = prevNode
        prevNode.next = node
        
       

    def remove(self, node):

        node.prev.next = node.next
        node.next.prev = node.prev
        
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)


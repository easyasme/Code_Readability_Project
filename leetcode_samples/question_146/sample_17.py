class ListNode:
    def __init__(self, key, val):
        self.val = val
        self.key = key
        self.next = None
        self.prev = None

class DLL:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0
    
    def add(self, key, val): # At tail
        node = ListNode(key, val)
        if not self.head:
            self.head = self.tail = node
            self.size += 1
            return node
       
        self.tail.next = node
        node.prev = self.tail
        
        self.tail = node
        
        self.size += 1
        
        
        return node
    
    def remove(self): # remove from head
        key = self.head.key
        if self.size <= 1:
            self.head = self.tail = None
        self.head = self.head.next
        self.prev = None
        self.size -= 1
        return key
    
    def shift_node_to_tail(self, node):
        
        if self.size == 1 or node == self.tail:
            return

        # remove node
        if node == self.head:
            self.remove()
            self.size += 1
        else:
            node.prev.next = node.next
            node.next.prev = node.prev
        
        node.next = None
        node.prev = self.tail
        self.tail.next = node
        self.tail = node
    
    def print(self):
        print("tail", self.tail.val)
        print("head", self.head.val)
        print("size", self.size)
        cur = self.head
        print("list")
        while cur and cur != self.tail:
            print(cur.val)
            cur = cur.next
        print(self.tail.val)
        



class LRUCache:

    def __init__(self, capacity: int):
        self.dll = DLL()
        self.map = {}
        self.capacity = capacity


    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self.dll.shift_node_to_tail(node)
        print("GET", key)
        print(self.dll.head.val)
        if self.dll.head.next:
            print("hnext", self.dll.head.next.val)
        return node.val
        

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self.map[key].val = value
            self.get(key)
            return
        node = self.dll.add(key, value)
        self.map[key] = node
        if self.dll.size > self.capacity:
            k = self.dll.remove()
            del self.map[k]
        print("PUT", key, value)
        print(self.dll.head.val)
        if self.dll.head.next:
            print("hnext", self.dll.head.next.val)
        



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
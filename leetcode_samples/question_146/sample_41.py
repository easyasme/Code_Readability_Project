class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.head = None
        self.tail = None
        self.mapi = {}
    
    def get(self, key: int) -> int:
        # print(key, self.head, self.tail)
        if key in self.mapi:
            self.remove(self.mapi[key])
            self.add(self.mapi[key])
            return self.mapi[key].val
        else:
            return -1

    def put(self, key: int, value: int) -> None:
        if key in self.mapi:
            node = self.mapi[key]
            self.remove(node)
            self.add(node)
            self.mapi[key].val = value
            return 
        node = Node(value)
        if len(self.mapi) < self.capacity:
            self.mapi[key] = node
            self.add(node)
        else:
            removed = self.removeLast()
            k = None
            for ke, val in self.mapi.items():
                if val == removed:
                    k = ke
                    break
            print(key, removed.val)
            del self.mapi[k]
            self.mapi[key] = node
            self.add(node)
    
    def add(self, node):
        if self.head is None:
            self.head = node
            self.tail = node
        self.head.left = node
        node.right = self.head
        self.head = node
        # print(self.head.val)
        
    def removeLast(self):
        last = self.tail
        if last == self.head:
            self.head = None
            self.tail = None
        last.left.right = None
        self.tail = last.left
        return last

    def remove(self, node):
        # print(node.val, self.head, self.tail)
        if self.head == self.tail:
            self.head = None
            self.tail = None
        if node == self.head:
            self.head = self.head.right
        elif node == self.tail:
            self.tail.left.right = None
            self.tail = self.tail.left
        else:

            left = node.left
            left.right = node.right
            node.right.left = left



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class ListNode:
    def __init__(self, key: int, val: int, prev=None, next=None):
        self.key = key
        self.val = val

class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.nodeMap = {}
        self.head = ListNode(-1, -1)
        self.tail = ListNode(-1,-1)
        self.tail.prev = self.head
        self.head.next = self.tail
    
    def add(self, node):
        tempFirst = self.head.next
        node.next = tempFirst
        tempFirst.prev = node
        self.head.next = node
        node.prev = self.head
        self.nodeMap[node.key] = node
        
        if len(self.nodeMap) > self.capacity:
            self.remove(self.tail.prev)
            
    def remove(self, node):
        del self.nodeMap[node.key]
        node.prev.next = node.next
        node.next.prev = node.prev

    def get(self, key: int) -> int:
        if key not in self.nodeMap:
            return -1
        else:
            node = self.nodeMap[key]
            self.remove(node)
            self.add(node)
            return node.val



    def put(self, key: int, value: int) -> None:
        if key in self.nodeMap:
            self.remove(self.nodeMap[key])
        node = ListNode(key, value)
        self.add(node)
class ListNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None

class LRUCache:

    # def __init__(self, capacity: int):
    #     self.size = capacity
    #     self.cache = {}
    #     self.next, self.before = {}, {}
    #     self.head, self.tail = '#', '$'
    #     self.connect(self.head, self.tail)

    # def connect(self, a, b):
    #     self.next[a], self.before[b] = b, a

    # def delete(self, key):
    #     self.connect(self.before[key], self.next[key])
    #     del self.before[key], self.next[key], self.cache[key]

    # def append(self, k, v):
    #     self.cache[k] = v
    #     self.connect(self.before[self.tail], k)
    #     self.connect(k, self.tail)
    #     if len(self.cache) > self.size:
    #         self.delete(self.next[self.head])

    # def get(self, key: int) -> int:
    #     if key not in self.cache: return -1
    #     val = self.cache[key]
    #     self.delete(key)
    #     self.append(key, val)
    #     return val

    # def put(self, key: int, value: int) -> None:
    #     if key in self.cache: self.delete(key)
    #     self.append(key, value)
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dic = {}
        self.head = ListNode(-1, -1)
        self.tail = ListNode(-1, -1)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get(self, key: int) -> int:
        print("get", key)
        if key not in self.dic:
            return -1
        node = self.dic[key]
        self.remove(node)
        self.add(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        print("put", key, value)
        if key not in self.dic:
            node = ListNode(key, value)
            self.dic[key] = node
            self.add(node)
        else:
            node = self.dic[key]
            node.val = value
            self.remove(node)
            self.add(node)
        if len(self.dic) > self.capacity:
            del self.dic[self.head.next.key]
            self.remove(self.head.next)

    def add(self, node):
        print("add", node.key, node.val)
        prev = self.tail.prev
        prev.next = node
        node.prev = prev
        node.next = self.tail
        self.tail.prev = node

    def remove(self, node):
        print("remove", node.key, node.val)
        node.prev.next = node.next
        node.next.prev = node.prev


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
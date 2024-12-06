class Node:
    key = 0
    val = 0
    nxt = None
    prv = None
    def __init__(self, k, v):
        self.key = k
        self.val = v

class LinkedList:
    head = None
    tail = None
    g = {}
    size = 0
    def __init__(self):
        self.head = None
        self.tail = None
        self.g = {}
        size = 0 
    def getSize(self):
        return self.size 
    def pop(self):
        self.size -= 1
        key = self.head.key

        # tail is also head
        if (self.tail == self.head):
            self.head = None
            self.tail = None
        # tail is not head
        else:
            self.head.nxt.prv = None
            self.head = self.head.nxt
        self.g.pop(key, None)
    def remove(self, key):
        self.size -= 1
        node = self.g[key]
        newNode = Node(node.key, node.val)
        # node is head and tail
        if (node == self.head and node == self.tail):
            self.head = None
            self.tail = None
        # node is head
        elif (node == self.head):
            self.head.nxt.prv = None
            self.head = self.head.nxt
        # node is tail
        elif (node == self.tail):
            self.tail.prv.nxt = None
            self.tail = self.tail.prv
        # node has a nxt and prv
        else:
            node.nxt.prv = node.prv
            node.prv.nxt = node.nxt
        self.g.pop(key, None)
        return newNode
    def add(self, key, val):
        node = Node(key, val)
        self.g[key] = node
        self.size += 1

        # No tail/head
        if (self.tail == None and self.head == None):
            self.tail = node
            self.head = node
        # tail == head
        elif (self.tail == self.head):
            print("a")
            self.head.nxt = node
            node.prv = self.head
            self.tail = node
        # tail != head
        else:
            self.tail.nxt = node
            node.prv = self.tail
            self.tail = node
    def print(self):
        return
        gArr = []
        for k in self.g.keys():
            gArr.append([k, self.g[k].val])
        print(gArr)

        arr = []
        temp = self.head
        while (temp):
            arr.append(temp.val)
            temp = temp.nxt
        print(arr)

        arr = []
        temp = self.tail
        while (temp):
            arr.insert(0, temp.val)
            temp = temp.prv
        print(arr)
        print('---')
    def contains(self, key):
        return key in self.g.keys()

class LRUCache:
    ll = None
    cap = 0

    def __init__(self, capacity: int):
        self.ll = LinkedList()
        self.cap = capacity
        

    def get(self, key: int) -> int:
        # print('get ' + str(key))
        if (not self.ll.contains(key)): return -1
        node = self.ll.remove(key)
        self.ll.add(key, node.val)
        self.ll.print()
        return node.val
        

    def put(self, key: int, value: int) -> None:
        # print('put ' + str(key) + ',  ' + str(value))
        # key already in list
        if (self.ll.contains(key)):
            node = self.ll.remove(key)
            self.ll.add(key, value)
            return 
        
        # too many elements. Need to evict one
        if (self.cap == self.ll.getSize()):
            self.ll.pop()

        self.ll.add(key, value)
        # self.ll.print()


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
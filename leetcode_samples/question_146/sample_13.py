class LRUCache:
    class Node:
        def __init__(self, leftNode, rightNode, val, key):
            self.leftNode = leftNode
            self.rightNode = rightNode
            self.val = val
            self.key = key

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.head = None
        self.tail = None

    def refreshNode(self, key):
        if self.cache[key] is self.tail:
            return 
        if self.cache[key] is self.head:
            self.head = self.cache[key].rightNode
            self.head.leftNode = None
        else:
            self.cache[key].leftNode.rightNode = self.cache[key].rightNode
            self.cache[key].rightNode.leftNode = self.cache[key].leftNode
        self.cache[key].leftNode = self.tail
        self.cache[key].rightNode = None
        self.tail.rightNode = self.cache[key]
        self.tail = self.cache[key]

    def get(self, key: int) -> int:
        # self.printState()
        print("get ", key)
        if key in self.cache:
            self.refreshNode(key)
            return self.cache[key].val
        return -1

    def put(self, key: int, value: int) -> None:
        # self.printState()
        print("put ",key)
        # empty
        if not self.cache:
            self.cache[key] = self.Node(None, None, value, key)
            self.head = self.cache[key]
            self.tail = self.cache[key]
            return
        if key in self.cache:
            self.cache[key].val = value
            self.refreshNode(key)
            return
        elif len(self.cache) == self.capacity:
            self.cache.pop(self.head.key)
            self.head = self.head.rightNode
        if not self.cache:
            self.cache[key] = self.Node(None, None, value, key)
            self.head = self.cache[key]
        else:
            self.cache[key] = self.Node(self.tail, None, value, key)
            self.tail.rightNode = self.cache[key]
        self.tail = self.cache[key]

    def printState(self):
        currentNode = self.head
        while currentNode != None:
            self.printNode(currentNode)
            currentNode = currentNode.rightNode

        
    def printNode(self, node):
        print(f"key: {node.key} value: {node.val}")




# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class LRUCache:

    def __init__(self, capacity: int):
        self.hashmap = {} # maps key to node
        self.capacity = capacity
        self.currentCount = 0

        self.LRU = Node("LRU")
        self.MRU = Node("MRU")
        self.LRU.next = self.MRU
        self.MRU.prev = self.LRU

    def get(self, key: int) -> int:
        # print(self.hashmap)
        # self.printNode()
        if key not in self.hashmap:
            return -1

        nodeToGet = self.hashmap[key]

        nodeToGet.remove()
        self.addToFront(nodeToGet)
        return nodeToGet.val

    def put(self, key: int, value: int) -> None:
        if key in self.hashmap:
            nodeToRemove = self.hashmap.get(key)
            nodeToRemove.remove()

        elif self.currentCount >= self.capacity:
            for k, v in self.hashmap.items():
                if v == self.LRU.next:
                    del self.hashmap[k]
                    break
            self.LRU.next.remove()

        nodeToAdd = Node(value)
        self.addToFront(nodeToAdd)
        self.hashmap[key] = nodeToAdd
        # print(key, self.hashmap[key])

        self.currentCount = len(self.hashmap)

    def addToFront(self, node):
        node.prev = self.MRU.prev
        node.next = self.MRU
        
        self.MRU.prev.next = node
        self.MRU.prev = node

    def printNode(self):
        ptr = self.LRU
        while ptr:
            print(ptr.val)
            ptr = ptr.next
        
class Node:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None

    def remove(self):
        self.prev.next = self.next
        self.next.prev = self.prev

        return self

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
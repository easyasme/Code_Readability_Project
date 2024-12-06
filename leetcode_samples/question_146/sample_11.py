class dList:

    def __init__(self, key=None, value=None, nextNode=None, prevNode=None):

        self.key = key
        self.value = value
        self.next = nextNode
        self.prev = prevNode

class LRUCache:

    def __init__(self, capacity: int):

        self.capacity = capacity
        self.total = 0

        self.keys = {}

        self.startNode = dList(key="start", value="start")
        self.endNode = dList(key="end", value="end")

        self.startNode.next = self.endNode
        self.endNode.prev = self.startNode 
        

    def get(self, key: int) -> int:


        if key in self.keys:
            value = self.keys[key][0]
            self.removeNode(key)
            self.addNode(key, value)
            return value
        
        else:
            return -1
        

    def put(self, key: int, value: int) -> None:


        if key in self.keys:
            
            self.removeNode(key)
            self.addNode(key, value)
            return
        
        if self.total < self.capacity:

            self.addNode(key, value)

        else:

            remNode = self.startNode.next
            remKey = remNode.key
            self.removeNode(remKey)
            self.addNode(key, value)

    def removeNode(self, key):

        curnode = self.keys[key][1]
        prevnode = curnode.prev
        nextnode = curnode.next
        prevnode.next = nextnode
        nextnode.prev = prevnode
        del curnode
        del self.keys[key]

        self.total -= 1

    def addNode(self, key, value):

        curnode = dList(key=key, value=value)

        nextnode = self.endNode
        prevnode = self.endNode.prev
        prevnode.next = curnode
        curnode.next = nextnode
        nextnode.prev = curnode
        curnode.prev = prevnode

        self.keys[key] = [value, curnode]

        self.total += 1
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
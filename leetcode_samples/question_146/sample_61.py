class Node:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None

    def __repr__(self):
        return "Node: " + str(self.val)

class LRUCache:
    def __init__(self, capacity: int):
        self.map = {}
        self.capacity = capacity

        self.head = Node(-1)
        self.tail = Node(-1)

        # Interlinking head and tail
        self._interLink(self.head, self.tail)

        # self._showLL()

    def get(self, key: int) -> int:
        # print("\n ==== GET =============")

        if key in self.map:
            node = self.map[key]
            self._remove(node)
            self._add(node)

            # self._showLL()

            return node.val
        return -1


    def put(self, key: int, value: int) -> None:
        # print("\n ==== PUT ============= ", key, value)
        
        if key in self.map:
            node = self.map[key]
            self._remove(node)

        node = Node(value)
        self.map[key] = node
        self._add(node)

        if len(self.map) > self.capacity:
            lastNode = self.head.next

            self._remove(lastNode)
            
            for x in self.map: # TODO: O(n) -> O(1)
                if self.map[x] == lastNode:
                    del self.map[x]
                    break

        # self._showLL()

    def _remove(self, node):
        self._interLink(node.prev, node.next)
    
    def _add(self, node): # Add node before tail
        self._interLink(self.tail.prev, node)
        self._interLink(node, self.tail)
    
    def _interLink(self, node1, node2):
        node1.next = node2
        node2.prev = node1

    def _showLL(self):
        print(self.map)
        curr = self.head

        print("LL : ", end="")
        while curr != None:
            print(curr, end=" -> ")
            curr = curr.next
        print()

        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
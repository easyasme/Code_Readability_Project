class Node:
    def __init__(self, key: int, val: int, prev, next): 
        self.key = key
        self.val = val
        self.next = next
        self.prev = prev


class LRUCache:

    def __init__(self, capacity: int):
        self.map = {}
        self.head = Node(-1, 0, None, None)
        self.capacity = capacity
        self.current_size = 0
        self.tail = self.head

    def get(self, key: int) -> int:
        if key in self.map and self.map[key] is not None:
            # update links of prev and next nodes
            node = self.map[key]
            if node != self.tail:
                print("GET", key)
                prev = node.prev
                print("prev val", prev.val)
                next = node.next
                prev.next = next

                next.prev = prev

                # update tail
                self.tail.next = node
                node.next = None
                node.prev = self.tail
                self.tail = node
                print(self.head.next.key if self.head.next else None)
            return self.tail.val
        return -1
        

    def put(self, key: int, value: int) -> None:

        # add node to tail
        if self.get(key) != -1:
            self.map[key].val = value
        else:
            if self.tail == self.head:
                self.map[key] = Node(key, value, self.head, None)
                self.head.next = self.map[key]
            else:
                self.map[key] = Node(key, value, self.tail, None)
            self.tail.next = self.map[key]
            self.tail = self.map[key]
            self.current_size += 1


        # new_node = self.map[key]
        
        # self.tail.next = new_node
        # self.tail = new_node
        print(key, value, self.current_size)
        # check if over capacity first
        if self.current_size > self.capacity:
            # evict LRU
            # print(self.head.key, self.head.val, self.head.n÷ext)
            to_remove = self.head.next
            print(to_remove.key, to_remove.val)
            self.map[to_remove.key] = None
            self.head.next = to_remove.next
            to_remove.next.prev = self.head
            self.current_size -= 1
        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
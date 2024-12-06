class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:

    def __init__(self, capacity: int):
        self.mapping = {} # key, [value, Node]
        self.capacity = capacity
        self.size = 0
        self.head = None
        self.tail = None

    def add_to_list(self, node):
        tail_node = self.tail
        tail_node.next = node
        node.prev = tail_node
        self.tail = node
        self.tail.next = None

    
    def update_node(self, node):
        if node == self.tail: 
            return
        elif node == self.head:
            self.head = self.head.next
            self.head.prev = None
            self.add_to_list(node)
        elif node != self.tail and node != self.head:
            prev_node = node.prev # Node 2 with value 1
            next_node = node.next # None

            print("a:", self.tail.value)
            print("b:", node.value)

            prev_node.next = next_node
            next_node.prev = prev_node
            self.add_to_list(node)

    def get(self, key: int) -> int:

        if key not in self.mapping: return -1
        print("this is key", key)
        
        if self.head:
            print("head_key", self.head.key)
            print("head_val", self.head.value)
            print(self.head.next)

        value, node = self.mapping[key] # 2 and Node 3
        
        self.update_node(node)

        return value


    def put(self, key: int, value: int) -> None:
        print(self.size)
        print(self.capacity)
        if not self.head: 
            print("hello")
            curr_node = Node(key, value)
            self.head = curr_node
            self.tail = self.head
            self.mapping[key] = [value, curr_node]
            self.size += 1
            print("head", self.head.value)
        elif key not in self.mapping and self.size == self.capacity: 
            if self.head == self.tail:
                evict_node = self.head
                del self.mapping[evict_node.key]

                node = Node(key, value)
                self.head = node
                self.tail = self.head
                self.mapping[key] = [value, node]
            else:
                # always evict head node
                evict_node = self.head
                del self.mapping[evict_node.key]
                self.head = evict_node.next

                print(evict_node.value)
                node = Node(key, value)
                
                self.add_to_list(node)
                self.mapping[key] = [value, node]

        elif key in self.mapping:
            node = self.mapping[key][1]
            print("you again?")
            if self.mapping[key][0] != value:
                self.mapping[key][0] = value
                node.value = value
            self.update_node(node)

        else: # not at capacity, we just need to add the value
            print("wah")
            node = Node(key, value)
            self.mapping[key] = [value, node]
            self.add_to_list(node)
            self.size += 1

            
# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
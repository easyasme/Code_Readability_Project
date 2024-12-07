
class LinkedNode:

    def __init__(self, prev, val, next):
        self.prev = prev
        self.val = val
        self.next = next

    def __print__(self):
        return f'Linked {(self.prev.val if self.prev is not None else None)} {self.val} {(self.next.val if self.next is not None else None)}'

    def print_list(self):        
        res = f'{self.val}'
        if self.prev is not None:
            res = f'prev: {self.prev.val},{res}'
        
        node = self.next
        i = 0
        while node is not None and i < 12:
            res = f'{res},{node.val}'
            if node.next is not None:
                if node.next.prev is None:
                    print(f'miss-match {node.next.val} != {node.val}')                      
                elif node.next.prev != node:
                    print(f'miss-match node.next.val {node.next.val} node.next.prev.val {node.next.prev.val} != node.val {node.val}')            
            node = node.next
            i += 1
        #while node is not None:
        #    res = f'{res},{node.val}'
        #    node = node.next
        return res


class LinkedList:

    def __init__(self):
        self.head = None
        self.tail = None

    def remove_head(self):
        old_head = self.head.val            
        self.head = self.head.next
        if self.head is not None:
            self.head.prev = None
        return old_head

    def remove(self, node):
        if node.next is not None and node.prev is not None:
            node.prev.next = node.next
            node.next.prev = node.prev
        else:
            if self.head is not None and node.val == self.head.val:
                self.remove_head()
            if node == self.tail:
                self.tail = self.tail.prev
                if self.tail is not None:
                    self.tail.next = None      

    def add_at_tail(self, node):
        node.prev = self.tail
        node.next = None
        if self.tail is not None:
            self.tail.next = node
        self.tail = node
        if self.head is None:
            self.head = node

    def move_to_tail(self, node):
        self.remove(node)
        self.add_at_tail(node)

    def print_list(self):  
        if self.head is None:
            return "[]"      
        res = f'{self.head.val}'
        if self.head.prev is not None:
            res = f'prev: {self.head.prev.val},{res}'
        
        node = self.head.next
        i = 0
        while node is not None and i < 12:
            res = f'{res},{node.val}'
            if node.next is not None:
                if node.next.prev is None:
                    print(f'miss-match {node.next.val} != {node.val}')                      
                elif node.next.prev != node:
                    print(f'miss-match node.next.val {node.next.val} node.next.prev.val {node.next.prev.val} != node.val {node.val}')            
            node = node.next
            i += 1
        #while node is not None:
        #    res = f'{res},{node.val}'
        #    node = node.next
        return res        



class LRUCache:

    def __init__(self, capacity: int):
        # Look-up by key
        self.look_up = {}
        self.usages_node_by_key = {}
        self.linked_list = LinkedList()
        self.capacity = capacity
        self.size = 0

    def get(self, key: int) -> int:
        value = self.look_up.get(key, -1)
        
        if value != -1:
            if key not in self.usages_node_by_key:
                print(f'put {key}')
                print(f'{list(self.usages_node_by_key.keys())}')
                print(f'{list(self.look_up.keys())}')   
            else:            
                node = self.usages_node_by_key[key]
                self.linked_list.move_to_tail(node)
        print(f'get {key} lru: {self.linked_list.print_list()}')                
        return value

    def put(self, key: int, value: int) -> None:                   
        if key in self.look_up:
            if key not in self.usages_node_by_key:
                print(f'put {key}')
                print(f'{list(self.usages_node_by_key.keys())}')
                print(f'{list(self.look_up.keys())}')   
            else:             
                node = self.usages_node_by_key[key]      
                self.linked_list.move_to_tail(node)    
        elif self.size == self.capacity:
            node = LinkedNode(None, key, None)
            self.usages_node_by_key[key] = node
            old_head = self.linked_list.head.val
            old_head_ = self.linked_list.remove_head()         
            if old_head not in self.usages_node_by_key or old_head not in self.look_up:
                print(f'old head {old_head}')
                print(f'{list(self.usages_node_by_key.keys())}')
                print(f'{list(self.look_up.keys())}')  
            else:            
                del self.usages_node_by_key[old_head]
                del self.look_up[old_head]
            self.linked_list.add_at_tail(node)
        else:
            self.size += 1
            node = LinkedNode(None, key, None)            
            self.usages_node_by_key[key] = node 

            self.linked_list.add_at_tail(node)     
        self.look_up[key] = value     
        print(f'put {key} lru: {self.linked_list.print_list()}')

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)

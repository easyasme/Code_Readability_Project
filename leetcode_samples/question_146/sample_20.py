class Node:
    def __init__(self, key, val, next, prev):
        self.key = key
        self.value = val
        self.prev = prev
        self.next = next

class LRUCache:

    def __init__(self, capacity: int):
        self.head = Node(-1, -1, None, None)
        self.tail = Node(-1, -1, None, None)
        self.tail.prev = self.head
        self.head.next = self.tail
        self.max_capacity = capacity
        self.curr_capacity = 0   
        self.node_map = dict() 

    def get(self, key: int) -> int:
        if key not in self.node_map:
            return -1

        existing_node = self.node_map[key]
        self.refresh_node(existing_node)
        return existing_node.value

    def put(self, key: int, value: int) -> None:
        if key not in self.node_map:
            next_temp = self.head.next
            print('next temp', next_temp.value)
            new_node = Node(key, value, None, None)
            new_node.next = next_temp
            new_node.prev = self.head
            next_temp.prev = new_node
            self.head.next = new_node
            self.node_map[key] = new_node
            self.curr_capacity += 1
        else: 
            existing_node = self.node_map[key]
            existing_node.value = value
            self.refresh_node(existing_node)

        # evict tail if we are above capacity:
        if self.curr_capacity > self.max_capacity:
            tail_node = self.tail.prev
            print('eviciting', tail_node.value)
            tail_node.next = None
            new_tail_node = tail_node.prev 
            print('new tail node', new_tail_node.value)
            new_tail_node.next = self.tail 
            self.tail.prev = new_tail_node 
            del self.node_map[tail_node.key]
            self.curr_capacity -= 1

        print(self.head.next.value, self.tail.prev.value, self.head.next.next.value)

    def refresh_node(self, existing_node):
         # update existing node place: 
        temp_next = existing_node.next
        existing_node.prev.next = temp_next
        temp_next.prev = existing_node.prev
        print('refresh', existing_node.value, temp_next.value, temp_next.prev.value)

        #move existing node to the front of the list:
        temp_head_next = self.head.next
        self.head.next = existing_node
        existing_node.prev = self.head 
        existing_node.next = temp_head_next
        temp_head_next.prev = existing_node



        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
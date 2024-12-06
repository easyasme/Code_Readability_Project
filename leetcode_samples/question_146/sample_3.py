"""
Linked list + hash table
"""
import dataclasses
from typing import TypeVar

ListNode = TypeVar('ListNode')

@dataclasses.dataclass
class ListNode:
    key: int
    val: int
    next: Optional[ListNode] = None
    prev: Optional[ListNode] = None

class List:
    def __init__(self):
        self.head = ListNode(-1, -1)
        self.tail = ListNode(-1, -1)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def remove(self, node: ListNode):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def add(self, node: ListNode):
        prev, next = self.head, self.head.next
        node.next, node.prev = next, prev
        next.prev, prev.next = node, node

class LRUCacheList:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.list = List()
        self.node_map = {}

    def get(self, key: int) -> int:
        if key in self.node_map:
            node = self.node_map[key]
            self.list.remove(node)
            self.list.add(node)
            return node.val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.node_map:
            node = self.node_map[key]
            node.val = value
            self.list.remove(node)
            self.list.add(node)
        else:
            node = ListNode(key, value)
            self.node_map[key] = node
            self.list.add(node)
            if len(self.node_map) > self.capacity:
                node_to_remove = self.list.tail.prev
                self.list.remove(node_to_remove)
                del self.node_map[node_to_remove.key]


from collections import OrderedDict

class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.ordered_dict = OrderedDict()

    def get(self, key: int) -> int:
        if key in self.ordered_dict:
            self.ordered_dict.move_to_end(key)
            return self.ordered_dict[key]
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.ordered_dict:
            self.ordered_dict.move_to_end(key)
            self.ordered_dict[key] = value
        else:
            self.ordered_dict[key] = value
            if len(self.ordered_dict) > self.capacity:
                self.ordered_dict.popitem(last=False)

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
class Node:
    __slots__ = ['val', 'prev', 'next']

    def __init__(self, val: int, prev=None, next=None):
        self.val = val
        self.prev = prev
        self.next = next

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.head = None
        self.tail = None
        self.d = {}  # Maps key -> Node

    def get(self, key: int) -> int:
        if key not in self.d:
            return -1
        node = self.d[key]
        # Move node to the head (most recently used)
        self._remove(node)
        self._append_to_head(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.d:
            # Remove existing node to update it
            node = self.d[key]
            self._remove(node)

        # Create new node
        node = Node(value)
        self.d[key] = node
        self._append_to_head(node)

        # If over capacity, remove the least recently used (tail)
        if len(self.d) > self.capacity:
            for k, v in self.d.items():
                if v == self.tail:
                    del self.d[k]
                    break
            self._remove(self.tail)

    def _append_to_head(self, node: Node):
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        node.prev = None

    def _remove(self, node: Node):
        # Update pointers in the doubly linked list
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev

        # Update head and tail pointers
        if node == self.head:
            self.head = node.next
        if node == self.tail:
            self.tail = node.prev

        node.prev = None
        node.next = None

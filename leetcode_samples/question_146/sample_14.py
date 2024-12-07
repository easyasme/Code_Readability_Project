class Node:
    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.lookup = {}
        self.head = Node()  # Dummy head
        self.tail = Node()  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def add(self, node):
        """Add a node at the end of the doubly linked list (before the tail)."""
        temp = self.tail.prev
        temp.next = node
        node.prev = temp
        node.next = self.tail
        self.tail.prev = node

    def remove(self, node):
        """Remove a node from the doubly linked list."""
        prev = node.prev
        next = node.next
        prev.next = next
        next.prev = prev

    def put(self, key, value):
        """Insert a key-value pair into the cache."""
        print("put", key, value)
        if key in self.lookup:
            # If the key exists, remove the old node.
            self.remove(self.lookup[key])
        elif len(self.lookup) == self.capacity:
            # If the cache is full, remove the least recently used item.
            lru_node = self.head.next  # LRU is always right after the head.
            self.remove(lru_node)
            del self.lookup[lru_node.key]

        # Add the new node to the cache and list.
        new_node = Node(key, value)
        self.add(new_node)
        self.lookup[key] = new_node

    def get(self, key):
        """Retrieve a value by key."""
        print("get", key)
        if key in self.lookup:
            # Move the accessed node to the end (most recently used).
            node = self.lookup[key]
            self.remove(node)
            self.add(node)
            return node.val
        else:
            return -1  # Key not found
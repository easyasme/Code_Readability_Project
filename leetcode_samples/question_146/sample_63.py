class DoubleLinkedListNode:
    def __init__(self, key, val, prev=None, nxt=None):
        self.key = key
        self.val = val
        self.prev = prev
        self.nxt = nxt

class LRUCache:

    def __init__(self, capacity: int):
        self.keymap = {}
        self.ll_h = None
        self.capacity = capacity

    def update(self, ll_node):
        if ll_node.prev:
            ll_node.prev.nxt = ll_node.nxt
            if ll_node.nxt:
                ll_node.nxt.prev = ll_node.prev
            prev_head = self.ll_h
            prev_head.prev = ll_node
            ll_node.prev = None
            ll_node.nxt = prev_head
            self.ll_h = ll_node

    def get(self, key: int) -> int:
        if key in self.keymap:
            ll_node = self.keymap[key]
            self.update(ll_node)
            return ll_node.val
        
        return -1

    def put(self, key: int, value: int) -> None:
        ll_node = self.keymap.get(key, None)
        if ll_node: 
            ll_node.val = value
            self.update(ll_node)
            return
        
        ll_node = DoubleLinkedListNode(key, value, None, self.ll_h)
        if self.ll_h:
            self.ll_h.prev = ll_node
        self.ll_h = ll_node
        self.keymap[key] = ll_node

        if len(self.keymap) > self.capacity:
            current = self.ll_h
            while current.nxt: 
                current = current.nxt
            current.prev.nxt = None
            del self.keymap[current.key]

        


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
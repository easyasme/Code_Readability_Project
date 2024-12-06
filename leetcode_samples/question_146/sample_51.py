class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.mydict = {} # key -> val per il retrieve normale
        self.prioritydict = {} # key - > priority  col max 
        self.reverse_p_dict = {} # priority -> key
        self.next_max_priority = 0 

    def get(self, key: int) -> int:
        try:
            output = self.mydict[key]
            del self.reverse_p_dict[self.prioritydict[key]]
            self.prioritydict[key] = self.next_max_priority 
            self.reverse_p_dict[self.next_max_priority] = key
            self.next_max_priority = self.next_max_priority +1
        except:
            output = -1
        return output

    def put(self, key: int, value: int) -> None:
        if self.get(key) != -1: #key is already present
            self.mydict[key] = value
        elif len(self.mydict.keys()) < self.capacity: # we can add the value
            self.mydict[key] = value
            self.prioritydict[key] = self.next_max_priority 
            self.reverse_p_dict[self.next_max_priority] = key
            self.next_max_priority = self.next_max_priority +1
        else: # we need to remove the last item first
            lowest_priority = min(self.reverse_p_dict.keys())
            lowest_key = self.reverse_p_dict[lowest_priority]
            del self.mydict[lowest_key]
            del self.prioritydict[lowest_key]
            del self.reverse_p_dict[lowest_priority]
            self.mydict[key] = value
            self.prioritydict[key] = self.next_max_priority 
            self.reverse_p_dict[self.next_max_priority] = key
            self.next_max_priority = self.next_max_priority +1

# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
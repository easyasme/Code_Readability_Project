class LRUCache:

    def __init__(self, capacity: int):
        # time -> key
        # key -> (value, time) - maintain unique value to each key
        self.cur_time = 0
        self.capacity = capacity
        self.time_key_map = {}
        self.key_value_map = {}
        

    def get(self, key: int) -> int:
        self.cur_time += 1
        if key in self.key_value_map.keys():
            (value, old_time) = self.key_value_map[key]
            
            del self.time_key_map[old_time]
            self.time_key_map[self.cur_time] = key
            self.key_value_map[key] = (value, self.cur_time)
            return value
        return -1

    def put(self, key: int, value: int) -> None:
        self.cur_time += 1

        if key in self.key_value_map:
            (old_value, old_time) = self.key_value_map[key]

            self.key_value_map[key] = (value, self.cur_time)

            del  self.time_key_map[old_time]
            self.time_key_map[self.cur_time] = key
            return 

        if len(self.key_value_map) == self.capacity:
            min_time_key = min(self.time_key_map)
            key_to_remove = self.time_key_map[min_time_key]

            # Remove the additional key
            _, time_to_remove = self.key_value_map[key_to_remove]
            del self.key_value_map[key_to_remove]
            del self.time_key_map[time_to_remove]

        # Add the new key and value
        self.key_value_map[key] = (value, self.cur_time)
        self.time_key_map[self.cur_time] = key



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
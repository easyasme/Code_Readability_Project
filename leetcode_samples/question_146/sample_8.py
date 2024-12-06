class LRUCache:

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.dictionary = {
            -1: [None, None, -2], # oldest pointer w/ dummy value
            -2: [None, -1, None]  # newest pointer w/ dummy value
        } # [value, older key, newer key]

    def detach(self, item: List[int]):
        prevItem = self.dictionary[item[1]]
        prevItem[2] = item[2]

        nextItem = self.dictionary[item[2]]
        nextItem[1] = item[1]        

    def attach(self, item: List[int], key: int):
        item[1] = self.dictionary[-2][1]
        item[2] = -2

        newestItemKey = self.dictionary[-2][1]
        newestItem = self.dictionary[newestItemKey]
        newestItem[2] = key

        self.dictionary[-2][1] = key

    def promote(self, item: List[int], key: int):
        self.detach(item)
        self.attach(item, key)

    def get(self, key: int) -> int:
        item = self.dictionary.get(key, [-1, -1, -1])

        if item[0] >= 0:
            self.promote(item, key)

        # print(self.capacity, self.debug(), 'get', key)

        return item[0]

    def debug(self) -> str:
        forwards = []
        backwards = []

        keyNext = self.dictionary[-1][2]
        
        while keyNext >= 0:
            forwards.append(str(keyNext))
            keyNext = self.dictionary[keyNext][2]

        keyNext = self.dictionary[-2][1]

        while keyNext >= 0:
            backwards.append(str(keyNext))
            keyNext = self.dictionary[keyNext][1]

        return "Forwards: [" + ' '.join(forwards) + "] Backwards: [" + ' '.join(backwards) + "]"

    def put(self, key: int, value: int) -> None:
        item = self.dictionary.setdefault(key, [-1, -1, -1])

        if item[0] < 0:            
            if len(self.dictionary) - 2 > self.capacity: # evict oldest
                oldestItemKey = self.dictionary[-1][2]
                oldestItem = self.dictionary[oldestItemKey]
                self.dictionary[-1][2] = oldestItem[2]
                self.dictionary[oldestItem[2]][1] = -1
                del(self.dictionary[oldestItemKey])

            # insert as newest
            item[0] = value
            
            self.attach(item, key)
        else:
            item[0] = value
            self.promote(item, key)

        # print(self.capacity, len(self.dictionary) - 2, self.debug(), 'put', key, value)



# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)
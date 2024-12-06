class LRUCache:

    def __init__(self, capacity: int):
        self.D={}
        self.L=capacity
    def get(self, key: int) -> int:
        try:
            X=self.D[key]
            self.D[key]=self.D.pop(key)
        except:
            X=-1
        return X

    def put(self, key: int, value: int) -> None:
        #print(self.D,self.L)
        self.D[key]=value
        self.D[key]=self.D.pop(key)
        if len(self.D)>self.L:
            self.D.pop(list(self.D.keys())[0])
        #print(self.D)


# Your LRUCache object will be instantiated and called as such:
# obj = LRUCache(capacity)
# param_1 = obj.get(key)
# obj.put(key,value)